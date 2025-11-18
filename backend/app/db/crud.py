# backend/app/db/crud.py
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime
from typing import List, Optional
# --- JOB CRUD helpers (append to backend/app/db/crud.py) ---
from typing import Optional
from datetime import datetime
from app.db import models



def create_candidate(db: Session, name: str, email: Optional[str], phone: Optional[str], resume_text: Optional[str] = None, parsed_json: Optional[dict] = None):
    candidate = models.Candidate(
        name=name,
        email=email,
        phone=phone,
        resume_text=resume_text,
        parsed_json=parsed_json,
        created_at=datetime.utcnow()
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate

def get_candidate(db: Session, candidate_id: int):
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()

def list_candidates(db: Session, skip: int = 0, limit: int = 100) -> List[models.Candidate]:
    return db.query(models.Candidate).order_by(models.Candidate.created_at.desc()).offset(skip).limit(limit).all()

def update_candidate_resume_and_parsed(db: Session, candidate_id: int, resume_text: str, parsed_json: dict):
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        return None
    candidate.resume_text = resume_text
    candidate.parsed_json = parsed_json
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate

def create_job(db, title: str, description: Optional[str] = None):
    job = models.Job(
        title=title,
        description=description,
        created_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def list_jobs(db, skip: int = 0, limit: int = 100):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).offset(skip).limit(limit).all()


# --- INTERVIEW CRUD ---

def create_interview(
    db: Session,
    candidate_id: int,
    job_id: Optional[int] = None,
    scheduled_at: Optional[datetime] = None,
    interviewer: Optional[str] = None,
    notes: Optional[str] = None
):
    interview = models.Interview(
        candidate_id=candidate_id,
        job_id=job_id,
        scheduled_at=scheduled_at,
        interviewer=interviewer,
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def get_interview(db: Session, interview_id: int):
    return db.query(models.Interview).filter(models.Interview.id == interview_id).first()


def list_interviews(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
    upcoming_only: bool = False
) -> List[models.Interview]:
    query = db.query(models.Interview)
    
    if candidate_id:
        query = query.filter(models.Interview.candidate_id == candidate_id)
    
    if job_id:
        query = query.filter(models.Interview.job_id == job_id)
    
    if upcoming_only:
        query = query.filter(models.Interview.scheduled_at > datetime.utcnow())
    
    return query.order_by(models.Interview.scheduled_at.desc()).offset(skip).limit(limit).all()


def update_interview(
    db: Session,
    interview_id: int,
    scheduled_at: Optional[datetime] = None,
    interviewer: Optional[str] = None,
    notes: Optional[str] = None,
    job_id: Optional[int] = None
):
    interview = get_interview(db, interview_id)
    if not interview:
        return None
    
    if scheduled_at is not None:
        interview.scheduled_at = scheduled_at
    if interviewer is not None:
        interview.interviewer = interviewer
    if notes is not None:
        interview.notes = notes
    if job_id is not None:
        interview.job_id = job_id
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def update_interview_notes(db: Session, interview_id: int, notes: str):
    interview = get_interview(db, interview_id)
    if not interview:
        return None
    
    interview.notes = notes
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def delete_interview(db: Session, interview_id: int):
    interview = get_interview(db, interview_id)
    if interview:
        db.delete(interview)
        db.commit()
    return True

