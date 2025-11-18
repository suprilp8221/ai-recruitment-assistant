# backend/app/api/v1/ranking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud, models
from app.services import ranking as ranking_service
from app.core.exceptions import JobNotFoundException, CandidateNotFoundException, AIServiceException, DatabaseException
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/jobs/{job_id}/rank/{candidate_id}")
def rank_candidate_endpoint(job_id: int, candidate_id: int, db: Session = Depends(get_db)):
    """Rank a candidate against a job using AI."""
    try:
        logger.info(f"Ranking candidate {candidate_id} for job {job_id}")
        
        # Validate job exists
        job = crud.get_job(db=db, job_id=job_id)
        if not job:
            logger.warning(f"Job not found: {job_id}")
            raise JobNotFoundException(job_id)
        
        # Validate candidate exists
        candidate = crud.get_candidate(db=db, candidate_id=candidate_id)
        if not candidate:
            logger.warning(f"Candidate not found: {candidate_id}")
            raise CandidateNotFoundException(candidate_id)
        
        # Make sure parsed_json is present; if not, use resume_text as minimal input
        parsed = candidate.parsed_json or {
            "summary": (candidate.resume_text or "")[:1000],
            "skills": [],
            "experience": [],
            "education": []
        }
        
        # Call ranking service
        try:
            result = ranking_service.rank_candidate_for_job(parsed, job.description or "")
            logger.debug(f"Ranking result: {result}")
        except Exception as e:
            logger.error(f"AI ranking service failed: {str(e)}", exc_info=True)
            raise AIServiceException("Candidate ranking", str(e))
        
        # Save numeric score to candidate
        try:
            candidate.score = float(result.get("score", 0))
            db.add(candidate)
            db.commit()
            logger.info(f"Saved score {candidate.score} for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to save score: {str(e)}", exc_info=True)
            db.rollback()
            raise DatabaseException("update_candidate_score", str(e))
        
        return {
            "candidate_id": candidate.id,
            "job_id": job.id,
            "score": candidate.score,
            "details": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ranking: {str(e)}", exc_info=True)
        raise DatabaseException("rank_candidate", str(e))
