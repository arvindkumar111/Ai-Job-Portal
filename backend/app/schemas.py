from pydantic import BaseModel
from pydantic import Field
from typing import Optional

class RecommendedJob(BaseModel):
    id: int
    title: str
    company: str
    location: str
    source: str
    role_category: Optional[str] = None
    experience_required: Optional[str] = None
    similarity_score: float
    matched_skills: list[str] = []

class ResumeUploadResponse(BaseModel):
    extracted_skills: list[str]
    recommendations: list[RecommendedJob]
    resume_text: str
class JobOut(BaseModel):
    id: int
    source: str
    title: str
    company: str
    location: str
    description: str
    experience_required: Optional[str] = None
    tags: list[str] = []
    role_category: Optional[str] = None

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy Job object directly

class JobListResponse(BaseModel):
    total: int
    jobs: list[JobOut]

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    gemini_api_key: str = Field(..., min_length=10, max_length=200)
    question: str = Field(..., min_length=1, max_length=4000)
    job_id: Optional[int] = None          # set if user is viewing a specific job
    resume_text: Optional[str] = Field(None, max_length=20000)  # optional: pass resume context along
    conversation_history: list[ChatMessage] = Field(default_factory=list, max_length=12)

class ChatResponse(BaseModel):
    answer: str
    referenced_job_ids: list[int] = []
    status: str = "success"
    preview_jobs: list[dict] = []
