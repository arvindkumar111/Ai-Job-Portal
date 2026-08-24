from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Job
from app.schemas import JobListResponse, JobOut

router = APIRouter()

@router.get("", response_model=JobListResponse)
def list_jobs(
    source: str | None = Query(None, description="Filter by platform, e.g. LinkedIn"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job)

    if source:
        query = query.filter(func.lower(Job.source) == source.lower())

    total = query.count()
    jobs = query.offset((page - 1) * page_size).limit(page_size).all()

    return JobListResponse(total=total, jobs=jobs)

PRIMARY_SOURCES = ["LinkedIn", "Naukri", "Indeed", "Internshala"]

@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    rows = db.query(Job.source).distinct().all()
    all_sources = [r[0] for r in rows]
    primary = [s for s in PRIMARY_SOURCES if s in all_sources]
    other = sorted([s for s in all_sources if s not in PRIMARY_SOURCES])
    return {"primary_sources": primary, "other_sources": other}


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
