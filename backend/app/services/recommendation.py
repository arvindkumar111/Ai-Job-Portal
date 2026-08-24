from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Job
from app.services.embeddings import get_embedding

def get_job_recommendations(db: Session, resume_text: str, resume_skills: list[str], top_k: int = 10) -> list[dict]:
    """Embeds the resume, finds the top_k most semantically similar jobs
    using pgvector cosine distance, and enriches each with a tag-overlap
    score for explainability."""
    resume_embedding = get_embedding(resume_text)
    if resume_embedding is None:
        return []

    # pgvector's <=> operator computes cosine distance directly in SQL —
    # far more efficient than pulling all 45k rows into Python and
    # computing similarity manually.
    embedding_str = str(resume_embedding)
    query = text("""
        SELECT id, title, company, location, source, tags, role_category,
               experience_required, description,
               1 - (embedding <=> :resume_embedding) AS similarity
        FROM jobs
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> :resume_embedding
        LIMIT :top_k
    """)

    results = db.execute(query, {"resume_embedding": embedding_str, "top_k": top_k}).fetchall()

    recommendations = []
    resume_skills_lower = {s.lower() for s in resume_skills}

    for row in results:
        job_tags_lower = {t.lower() for t in (row.tags or [])}
        matched_skills = list(resume_skills_lower & job_tags_lower)

        recommendations.append({
            "id": row.id,
            "title": row.title,
            "company": row.company,
            "location": row.location,
            "source": row.source,
            "role_category": row.role_category,
            "experience_required": row.experience_required,
            "similarity_score": round(float(row.similarity), 3),
            "matched_skills": matched_skills,
        })

    return recommendations