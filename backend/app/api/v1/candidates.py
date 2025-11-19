# backend/app/api/v1/candidates.py
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, SessionLocal
from app.db import crud, models
from app import schemas
from app.services import resume_parser
from app.core.exceptions import CandidateNotFoundException, ResumeParsingException, DatabaseException
from app.core.security import validate_resume_file, sanitize_filename
from app.core.logging_config import get_logger
from app.core.auth_dependencies import get_current_user, require_recruiter_or_admin
from uuid import uuid4
from typing import List

router = APIRouter()
logger = get_logger(__name__)

# ensure uploads folder exists
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/candidates/upload")
async def upload_candidate(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_recruiter_or_admin)
):
    """
    Upload resume file (pdf/docx) with candidate basic info.
    We create DB row immediately and schedule a background task to extract text and parse.
    """
    logger.info(f"Uploading candidate: {name}, file: {file.filename}")
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        validate_resume_file(file)
        
        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)
        logger.debug(f"Sanitized filename: {safe_filename}")
        
        # Save initial candidate record (no resume_text yet)
        db = next(get_db())
        candidate = crud.create_candidate(db=db, name=name, email=email, phone=phone)
        logger.info(f"Candidate created with ID: {candidate.id}")
        db.close()

        # Save file to disk
        ext = os.path.splitext(safe_filename)[1].lower()
        fn = f"{uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, fn)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"File saved: {file_path}")

        # Schedule background processing
        background_tasks.add_task(process_resume_background, candidate.id, file_path)

        return {"status": "uploaded", "candidate_id": candidate.id}
        
    except Exception as e:
        logger.error(f"Error uploading candidate: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise DatabaseException("create_candidate", str(e))

def process_resume_background(candidate_id: int, file_path: str):
    """
    This runs in background (no request db session). Create a new session here.
    """
    logger.info(f"Background processing resume for candidate {candidate_id}")
    
    db = SessionLocal()
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".pdf"]:
            text = resume_parser.extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            text = resume_parser.extract_text_from_docx(file_path)
        else:
            # unknown type: read as bytes and decode
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                text = data.decode(errors="ignore")
            except Exception:
                text = ""
        
        if not text:
            logger.warning(f"No text extracted from resume for candidate {candidate_id}")

        # Use AI-powered parsing (with fallback to basic)
        parsed = resume_parser.parse_resume_text(text, use_ai=True)
        logger.debug(f"Parsed resume data for candidate {candidate_id}")
        
        # update candidate with resume_text and parsed_json
        crud.update_candidate_resume_and_parsed(db=db, candidate_id=candidate_id, resume_text=text, parsed_json=parsed)
        logger.info(f"Successfully processed resume for candidate {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error processing resume for candidate {candidate_id}: {str(e)}", exc_info=True)
    finally:
        db.close()

@router.get("/candidates", response_model=List[schemas.CandidateOut])
def get_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all candidates."""
    try:
        logger.debug(f"Listing candidates: skip={skip}, limit={limit}")
        items = crud.list_candidates(db=db, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(items)} candidates")
        return items
    except Exception as e:
        logger.error(f"Error listing candidates: {str(e)}", exc_info=True)
        raise DatabaseException("list_candidates", str(e))

@router.get("/candidates/{candidate_id}", response_model=schemas.CandidateOut)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific candidate by ID."""
    try:
        logger.debug(f"Fetching candidate: {candidate_id}")
        item = crud.get_candidate(db=db, candidate_id=candidate_id)
        if not item:
            logger.warning(f"Candidate not found: {candidate_id}")
            raise CandidateNotFoundException(candidate_id)
        logger.info(f"Retrieved candidate: {candidate_id}")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate {candidate_id}: {str(e)}", exc_info=True)
        raise DatabaseException("get_candidate", str(e))
