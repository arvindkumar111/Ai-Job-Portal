import google.generativeai as genai
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Job
from app.services.embeddings import get_embedding
from app.config import settings

SYSTEM_INSTRUCTIONS = """You are a helpful career assistant embedded in a job board.
Answer only using the information provided below (job descriptions, resume, conversation).
If the answer isn't in the provided context, say so honestly rather than guessing.
Be concise, specific, and practical."""

logger = logging.getLogger(__name__)


def make_preview_jobs(jobs: list[Job]) -> list[dict]:
    """Return only database-backed details that are safe to show during an AI outage."""
    return [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "source": job.source,
            "tags": (job.tags or [])[:3],
        }
        for job in jobs
    ]


def is_retryable_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(marker in message for marker in (
        "429", "resource_exhausted", "quota", "rate limit", "timeout",
        "timed out", "temporarily", "unavailable", "503", "500",
    ))


def can_try_fallback_model(error: Exception) -> bool:
    message = str(error).lower()
    return is_retryable_error(error) or any(marker in message for marker in (
        "model", "not found", "not supported",
    ))


def generate_with_retries(model_name: str, prompt: str, attempts: int = 3) -> str:
    """Retry only transient provider failures; other failures fail immediately."""
    last_error = None
    for attempt in range(attempts):
        try:
            model = genai.GenerativeModel(model_name, generation_config={"temperature": 0.3})
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as error:
            last_error = error
            if not is_retryable_error(error) or attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)
    raise last_error

def get_job_by_id(db: Session, job_id: int) -> Job | None:
    return db.query(Job).filter(Job.id == job_id).first()

def get_preview_jobs(db: Session, limit: int = 5) -> list[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()

def retrieve_relevant_jobs(db: Session, query: str, top_k: int = 5) -> list[Job]:
    """Same pgvector similarity pattern used for resume recommendations —
    reused here for broad, dataset-wide chat questions."""
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return []

    embedding_str = str(query_embedding)
    sql = text("""
        SELECT id FROM jobs
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
    """)
    rows = db.execute(sql, {"query_embedding": embedding_str, "top_k": top_k}).fetchall()
    job_ids = [r.id for r in rows]

    if not job_ids:
        return []
    return db.query(Job).filter(Job.id.in_(job_ids)).all()

def build_context(jobs: list[Job], resume_text: str | None) -> str:
    """Formats retrieved jobs + resume into a context block for the prompt.
    Truncates descriptions to keep token usage bounded across multiple jobs."""
    parts = []

    if resume_text:
        parts.append(f"CANDIDATE'S RESUME:\n{resume_text[:2000]}\n")

    for job in jobs:
        parts.append(
            f"JOB #{job.id}: {job.title} at {job.company} ({job.source})\n"
            f"Location: {job.location}\n"
            f"Experience required: {job.experience_required}\n"
            f"Tags: {', '.join(job.tags or [])}\n"
            f"Description: {job.description[:1500]}\n"
        )

    return "\n---\n".join(parts)

def answer_chat_question(
    db: Session,
    api_key: str,
    question: str,
    job_id: int | None,
    resume_text: str | None,
    conversation_history: list,
) -> dict:
    """Routes the question: job-specific questions use direct context (no
    retrieval needed); broad questions trigger pgvector retrieval first.
    This is the RAG decision point — retrieval only when it's actually needed."""

    retrieval_failed = False
    if job_id:
        job = get_job_by_id(db, job_id)
        jobs_for_context = [job] if job else []
        referenced_ids = [job.id] if job else []
    else:
        try:
            jobs_for_context = retrieve_relevant_jobs(db, question, top_k=5)
        except Exception:
            logger.exception("Job retrieval failed; continuing without semantic matching.")
            retrieval_failed = True
            try:
                jobs_for_context = get_preview_jobs(db)
            except Exception:
                logger.exception("Could not load jobs for an outage preview.")
                jobs_for_context = []
        referenced_ids = [j.id for j in jobs_for_context]

    preview_jobs = make_preview_jobs(jobs_for_context)

    if retrieval_failed and not resume_text:
        return {
            "answer": "I couldn't calculate matching roles right now. The AI assistant and job matching service are temporarily unavailable, but you can still explore the available roles below and try again shortly.",
            "referenced_job_ids": referenced_ids,
            "status": "unavailable",
            "preview_jobs": preview_jobs,
        }

    if not jobs_for_context and not resume_text:
        return {
            "answer": "I couldn't find enough job information to answer that confidently. Try asking about a specific role, its requirements, or your uploaded resume.",
            "referenced_job_ids": [],
            "status": "no_context",
            "preview_jobs": [],
        }

    context = build_context(jobs_for_context, resume_text)

    history_text = "\n".join(
        f"{msg.role.upper()}: {msg.content}" for msg in conversation_history[-6:]  # last 6 turns only
    )

    full_prompt = f"""{SYSTEM_INSTRUCTIONS}

CONTEXT:
{context}

CONVERSATION SO FAR:
{history_text}

USER'S QUESTION: {question}
"""

    try:
        genai.configure(api_key=api_key)
        answer = generate_with_retries(settings.llm_model, full_prompt)
        status = "success"
    except Exception as e:
        logger.warning("Primary chat model failed; attempting fallback where appropriate.", exc_info=True)
        if settings.fallback_llm_model != settings.llm_model and can_try_fallback_model(e):
            try:
                answer = generate_with_retries(settings.fallback_llm_model, full_prompt)
                return {
                    "answer": answer,
                    "referenced_job_ids": referenced_ids,
                    "status": "fallback",
                    "preview_jobs": preview_jobs,
                }
            except Exception:
                logger.exception("Fallback chat model failed.")
        return {
            "answer": "The AI assistant is temporarily unavailable. You can still explore the relevant roles below and try your question again shortly.",
            "referenced_job_ids": referenced_ids,
            "status": "unavailable",
            "preview_jobs": preview_jobs,
        }
    return {
        "answer": answer,
        "referenced_job_ids": referenced_ids,
        "status": status,
        "preview_jobs": preview_jobs,
    }
