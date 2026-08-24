from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.resume_parser import extract_resume_text
from app.services.skill_extraction import extract_skills_from_text
from app.services.recommendation import get_job_recommendations
from app.schemas import ResumeUploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = (".pdf", ".docx")
MAX_FILE_SIZE_MB = 5

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or ""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB.")

    is_pdf = filename.lower().endswith(".pdf") and file_bytes.startswith(b"%PDF-")
    is_docx = filename.lower().endswith(".docx") and file_bytes.startswith(b"PK")
    if not (is_pdf or is_docx):
        raise HTTPException(status_code=400, detail="The uploaded file does not match its file type.")

    resume_text = extract_resume_text(filename, file_bytes)
    if not resume_text or not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from this file. It may be scanned/image-based or corrupted."
        )

    skills = extract_skills_from_text(resume_text)
    recommendations = get_job_recommendations(db, resume_text, skills, top_k=10)

    return ResumeUploadResponse(
        extracted_skills=skills,
        recommendations=recommendations,
        resume_text=resume_text,
    )
