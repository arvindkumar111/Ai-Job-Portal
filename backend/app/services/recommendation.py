from sqlalchemy import text
from sqlalchemy.orm import Session


def get_keyword_recommendations(
    db: Session,
    resume_text: str,
    resume_skills: list[str],
    top_k: int = 10,
) -> list[dict]:
    """Return explainable recommendations without loading a local ML model."""
    if not resume_text or not resume_text.strip() or not resume_skills:
        return []

    skills = list(dict.fromkeys(skill.strip() for skill in resume_skills if skill.strip()))
    if not skills:
        return []

    conditions = []
    parameters = {"limit": max(top_k * 5, 30)}
    for index, skill in enumerate(skills):
        parameter = f"skill_{index}"
        parameters[parameter] = f"%{skill}%"
        conditions.append(
            f"(title ILIKE :{parameter} OR role_category ILIKE :{parameter} "
            f"OR :{parameter} = ANY(tags) OR description ILIKE :{parameter})"
        )

    rows = db.execute(text(f"""
        SELECT id, title, company, location, source, tags, role_category,
               experience_required, description
        FROM jobs
        WHERE {' OR '.join(conditions)}
        LIMIT :limit
    """), parameters).fetchall()

    scored = []
    for row in rows:
        title = (row.title or "").lower()
        role_category = (row.role_category or "").lower()
        tags = {tag.lower() for tag in (row.tags or [])}
        description = (row.description or "").lower()
        matched_skills = [
            skill for skill in skills
            if skill.lower() in title
            or skill.lower() in role_category
            or skill.lower() in tags
            or skill.lower() in description
        ]
        title_matches = sum(skill.lower() in title for skill in skills)
        tag_matches = sum(skill.lower() in tags for skill in skills)
        score = min(1.0, (len(matched_skills) / len(skills)) * 0.7 + title_matches * 0.2 + tag_matches * 0.1)
        if matched_skills:
            scored.append((score, row, matched_skills))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "id": row.id,
            "title": row.title,
            "company": row.company,
            "location": row.location,
            "source": row.source,
            "role_category": row.role_category,
            "experience_required": row.experience_required,
            "similarity_score": round(score, 3),
            "matched_skills": matched_skills,
        }
        for score, row, matched_skills in scored[:top_k]
    ]


def get_rag_recommendations(
    db: Session,
    resume_text: str,
    resume_skills: list[str],
    top_k: int = 10,
) -> list[dict]:
    """Original pgvector recommendation path, available when RAG is enabled."""
    from app.services.embeddings import get_embedding

    resume_embedding = get_embedding(resume_text)
    if resume_embedding is None:
        return []

    rows = db.execute(text("""
        SELECT id, title, company, location, source, tags, role_category,
               experience_required,
               1 - (embedding <=> :resume_embedding) AS similarity
        FROM jobs
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> :resume_embedding
        LIMIT :top_k
    """), {"resume_embedding": str(resume_embedding), "top_k": top_k}).fetchall()

    resume_skills_lower = {skill.lower() for skill in resume_skills}
    return [
        {
            "id": row.id,
            "title": row.title,
            "company": row.company,
            "location": row.location,
            "source": row.source,
            "role_category": row.role_category,
            "experience_required": row.experience_required,
            "similarity_score": round(float(row.similarity), 3),
            "matched_skills": [
                tag for tag in (row.tags or []) if tag.lower() in resume_skills_lower
            ],
        }
        for row in rows
    ]


def get_job_recommendations(
    db: Session,
    resume_text: str,
    resume_skills: list[str],
    top_k: int = 10,
) -> list[dict]:
    """Use keyword mode by default; RAG can be enabled with an environment variable."""
    from app.config import settings

    if settings.recommendation_mode.lower() == "rag":
        return get_rag_recommendations(db, resume_text, resume_skills, top_k)
    return get_keyword_recommendations(db, resume_text, resume_skills, top_k)
