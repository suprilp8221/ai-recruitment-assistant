# backend/app/api/v1/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app import schemas
from app.db import crud
from app.core.exceptions import JobNotFoundException, DatabaseException
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/jobs", response_model=schemas.JobOut)
def create_job_endpoint(payload: schemas.JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting."""
    try:
        logger.info(f"Creating job: {payload.title}")
        job = crud.create_job(db=db, title=payload.title, description=payload.description)
        logger.info(f"Job created with ID: {job.id}")
        return job
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}", exc_info=True)
        raise DatabaseException("create_job", str(e))

@router.get("/jobs", response_model=List[schemas.JobOut])
def list_jobs_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all job postings."""
    try:
        logger.debug(f"Listing jobs: skip={skip}, limit={limit}")
        items = crud.list_jobs(db=db, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(items)} jobs")
        return items
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}", exc_info=True)
        raise DatabaseException("list_jobs", str(e))

@router.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job_endpoint(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID."""
    try:
        logger.debug(f"Fetching job: {job_id}")
        job = crud.get_job(db=db, job_id=job_id)
        if not job:
            logger.warning(f"Job not found: {job_id}")
            raise JobNotFoundException(job_id)
        logger.info(f"Retrieved job: {job_id}")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}", exc_info=True)
        raise DatabaseException("get_job", str(e))
