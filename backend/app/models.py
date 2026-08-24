from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, func
from pgvector.sqlalchemy import Vector
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)          # "LinkedIn", "Naukri", etc.
    title = Column(String, nullable=False)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    experience_required = Column(String, nullable=True)  # e.g. "0-2 years", nullable = might be missing

    # dedup fingerprint — see dedup.py explanation later
    content_hash = Column(String, unique=True, index=True)

    # AI-enrichment output (requirement 2)
    tags = Column(ARRAY(String), default=[])      # e.g. ["Python", "Machine Learning", "Fresher"]
    role_category = Column(String, nullable=True) # e.g. "Backend Engineer"

    # embedding for semantic search (requirement 3 & 4)
    embedding = Column(Vector(384))  # dimension must match your embedding model's output size
    
    created_at = Column(DateTime, server_default=func.now())