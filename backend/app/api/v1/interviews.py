# backend/app/api/v1/interviews.py
"""
Interview management endpoints.
Handles scheduling, updating, and managing interview sessions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app import schemas
from app.db import crud
from app.core.exceptions import (
    CandidateNotFoundException,
    JobNotFoundException,
    InterviewNotFoundException,
    DatabaseException,
    InvalidScheduleException
)
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/interviews", response_model=schemas.InterviewOut, status_code=201)
def create_interview(
    payload: schemas.InterviewCreate,
    db: Session = Depends(get_db)
):
    """
    Schedule a new interview.
    Links a candidate to a job with scheduled datetime and interviewer.
    """
    try:
        logger.info(f"Creating interview for candidate {payload.candidate_id}")
        
        # Validate scheduled time is in the future
        if payload.scheduled_at and payload.scheduled_at < datetime.utcnow():
            raise InvalidScheduleException("Interview time must be in the future")
        
        # Validate candidate exists
        candidate = crud.get_candidate(db=db, candidate_id=payload.candidate_id)
        if not candidate:
            logger.warning(f"Candidate not found: {payload.candidate_id}")
            raise CandidateNotFoundException(payload.candidate_id)
        
        # Validate job exists if provided
        if payload.job_id:
            job = crud.get_job(db=db, job_id=payload.job_id)
            if not job:
                logger.warning(f"Job not found: {payload.job_id}")
                raise JobNotFoundException(payload.job_id)
        
        interview = crud.create_interview(
            db=db,
            candidate_id=payload.candidate_id,
            job_id=payload.job_id,
            scheduled_at=payload.scheduled_at,
            interviewer=payload.interviewer,
            notes=payload.notes
        )
        logger.info(f"Interview created with ID: {interview.id}")
        return interview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating interview: {str(e)}", exc_info=True)
        raise DatabaseException("create_interview", str(e))


@router.get("/interviews", response_model=List[schemas.InterviewOut])
def list_interviews(
    skip: int = 0,
    limit: int = 100,
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
    upcoming_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all interviews with optional filters.
    
    Query params:
    - candidate_id: Filter by candidate
    - job_id: Filter by job
    - upcoming_only: Only show future interviews
    """
    try:
        logger.debug(f"Listing interviews: skip={skip}, limit={limit}, candidate_id={candidate_id}, job_id={job_id}")
        interviews = crud.list_interviews(
            db=db,
            skip=skip,
            limit=limit,
            candidate_id=candidate_id,
            job_id=job_id,
            upcoming_only=upcoming_only
        )
        logger.info(f"Retrieved {len(interviews)} interviews")
        return interviews
    except Exception as e:
        logger.error(f"Error listing interviews: {str(e)}", exc_info=True)
        raise DatabaseException("list_interviews", str(e))


@router.get("/interviews/{interview_id}", response_model=schemas.InterviewOut)
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    """Get specific interview by ID."""
    try:
        logger.debug(f"Fetching interview: {interview_id}")
        interview = crud.get_interview(db=db, interview_id=interview_id)
        if not interview:
            logger.warning(f"Interview not found: {interview_id}")
            raise InterviewNotFoundException(interview_id)
        logger.info(f"Retrieved interview: {interview_id}")
        return interview
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview {interview_id}: {str(e)}", exc_info=True)
        raise DatabaseException("get_interview", str(e))


@router.put("/interviews/{interview_id}", response_model=schemas.InterviewOut)
def update_interview(
    interview_id: int,
    payload: schemas.InterviewUpdate,
    db: Session = Depends(get_db)
):
    """
    Update interview details.
    Can update scheduled time, interviewer, or notes.
    """
    interview = crud.get_interview(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Validate job if being updated
    if payload.job_id is not None:
        if payload.job_id > 0:
            job = crud.get_job(db=db, job_id=payload.job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
    
    updated = crud.update_interview(
        db=db,
        interview_id=interview_id,
        scheduled_at=payload.scheduled_at,
        interviewer=payload.interviewer,
        notes=payload.notes,
        job_id=payload.job_id
    )
    return updated


@router.delete("/interviews/{interview_id}", status_code=204)
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    """Cancel/delete an interview."""
    interview = crud.get_interview(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    crud.delete_interview(db=db, interview_id=interview_id)
    return None


@router.put("/interviews/{interview_id}/notes", response_model=schemas.InterviewOut)
def update_interview_notes(
    interview_id: int,
    payload: schemas.InterviewNotesUpdate,
    db: Session = Depends(get_db)
):
    """
    Add or update interview feedback/notes.
    Useful for adding notes after interview is completed.
    """
    interview = crud.get_interview(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    updated = crud.update_interview_notes(
        db=db,
        interview_id=interview_id,
        notes=payload.notes
    )
    return updated


@router.get("/candidates/{candidate_id}/interviews", response_model=List[schemas.InterviewOut])
def get_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Get all interviews for a specific candidate."""
    candidate = crud.get_candidate(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    interviews = crud.list_interviews(
        db=db,
        candidate_id=candidate_id,
        skip=0,
        limit=100
    )
    return interviews


@router.get("/jobs/{job_id}/interviews", response_model=List[schemas.InterviewOut])
def get_job_interviews(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get all interviews scheduled for a specific job."""
    job = crud.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    interviews = crud.list_interviews(
        db=db,
        job_id=job_id,
        skip=0,
        limit=100
    )
    return interviews
