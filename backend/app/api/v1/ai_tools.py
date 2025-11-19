# backend/app/api/v1/ai_tools.py
"""
AI-powered tools API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.db.database import get_db
from app.db import crud, models
from app.services import interview_questions, ai_feedback, resume_optimizer
from app.core.logging_config import get_logger
from app.core.auth_dependencies import get_current_user, require_interviewer_or_above

router = APIRouter()
logger = get_logger(__name__)


class GenerateQuestionsRequest(BaseModel):
    """Request model for generating interview questions."""
    job_id: int = Field(..., description="Job ID")
    candidate_id: int = Field(..., description="Candidate ID")
    count: int = Field(10, ge=1, le=20, description="Number of questions (1-20)")
    difficulty: Optional[str] = Field("medium", description="Difficulty level: easy, medium, hard")
    question_types: Optional[List[str]] = Field(
        default=["technical", "behavioral"],
        description="Types of questions: technical, behavioral, situational, culture-fit"
    )


class QuestionResponse(BaseModel):
    """Single question response."""
    question: str
    type: str
    difficulty: str
    category: str
    follow_up: Optional[str] = None


class GenerateQuestionsResponse(BaseModel):
    """Response model for generated questions."""
    job_id: int
    job_title: str
    candidate_id: int
    candidate_name: str
    total_questions: int
    experience_level: str
    questions: List[QuestionResponse]
    categorized: dict
    model_used: str


@router.post("/ai/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_interview_questions_endpoint(
    request: GenerateQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_interviewer_or_above)
):
    """
    Generate personalized interview questions for a candidate and job.
    
    This endpoint uses OpenAI to generate relevant interview questions based on:
    - Job requirements and description
    - Candidate's skills and experience from their resume
    - Specified difficulty level and question types
    
    **Example Request:**
    ```json
    {
      "job_id": 1,
      "candidate_id": 2,
      "count": 10,
      "difficulty": "medium",
      "question_types": ["technical", "behavioral"]
    }
    ```
    
    **Returns:**
    - Personalized interview questions categorized by type
    - Questions tailored to the candidate's background
    - Mix of technical and behavioral questions
    """
    logger.info(f"Generating questions for candidate {request.candidate_id} and job {request.job_id}")
    
    try:
        # Fetch job
        job = crud.get_job(db=db, job_id=request.job_id)
        if not job:
            logger.warning(f"Job not found: {request.job_id}")
            raise HTTPException(status_code=404, detail=f"Job with ID {request.job_id} not found")
        
        # Fetch candidate
        candidate = crud.get_candidate(db=db, candidate_id=request.candidate_id)
        if not candidate:
            logger.warning(f"Candidate not found: {request.candidate_id}")
            raise HTTPException(status_code=404, detail=f"Candidate with ID {request.candidate_id} not found")
        
        # Determine experience level from candidate data or default to medium
        experience_level = "mid"  # Default
        if candidate.parsed_json:
            # Try to infer from parsed data
            years_exp = candidate.parsed_json.get("years_of_experience", 0)
            if years_exp < 2:
                experience_level = "junior"
            elif years_exp > 5:
                experience_level = "senior"
        
        # Map difficulty to experience level if needed
        if request.difficulty:
            difficulty_map = {
                "easy": "junior",
                "medium": "mid",
                "hard": "senior"
            }
            experience_level = difficulty_map.get(request.difficulty.lower(), experience_level)
        
        # Extract skills from parsed data
        skills = []
        if candidate.parsed_json and "skills" in candidate.parsed_json:
            skills = candidate.parsed_json["skills"]
        
        # Get resume text
        resume_text = candidate.resume_text or "No resume text available"
        
        # Generate questions
        result = interview_questions.generate_questions_for_candidate_job(
            candidate_name=candidate.name,
            job_title=job.title,
            job_description=job.description,
            resume_text=resume_text,
            skills=skills,
            experience_level=experience_level,
            count=request.count
        )
        
        # Build response
        response = GenerateQuestionsResponse(
            job_id=job.id,
            job_title=job.title,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            total_questions=result["total_questions"],
            experience_level=result["experience_level"],
            questions=[QuestionResponse(**q) for q in result["questions"]],
            categorized=result["categorized"],
            model_used=result["model_used"]
        )
        
        logger.info(f"Successfully generated {result['total_questions']} questions")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


@router.get("/ai/question-templates/{experience_level}")
async def get_question_templates(
    experience_level: str,
    current_user: models.User = Depends(get_current_user)
):
    """
    Get template questions for a specific experience level.
    
    This endpoint returns pre-defined question templates without requiring
    a specific candidate or job. Useful for previewing questions or when
    OpenAI is not available.
    
    **Parameters:**
    - experience_level: junior, mid, or senior
    
    **Returns:**
    - List of template questions for the specified level
    """
    logger.info(f"Fetching question templates for level: {experience_level}")
    
    valid_levels = ["junior", "mid", "senior"]
    if experience_level.lower() not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid experience level. Must be one of: {', '.join(valid_levels)}"
        )
    
    # Use fallback generator to get templates
    result = interview_questions._generate_fallback_questions(
        count=10,
        level=experience_level.lower()
    )
    
    return {
        "experience_level": experience_level,
        "total_questions": result["total_questions"],
        "questions": result["questions"],
        "categorized": result["categorized"]
    }


# ============================================================================
# Interview Feedback Analysis Endpoints
# ============================================================================

class AnalyzeFeedbackRequest(BaseModel):
    """Request model for analyzing interview feedback."""
    interview_notes: str = Field(..., min_length=10, description="Interview notes/feedback to analyze")


class FeedbackAnalysisResponse(BaseModel):
    """Response model for feedback analysis."""
    interview_id: int
    candidate_name: str
    job_title: str
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str  # hire, maybe, no-hire
    confidence_score: int  # 0-100
    reasoning: str
    next_steps: List[str]
    overall_assessment: str
    technical_skills_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_skills_rating: Optional[int] = Field(None, ge=1, le=5)
    culture_fit_rating: Optional[int] = Field(None, ge=1, le=5)
    model_used: str


@router.post("/ai/interviews/{interview_id}/analyze-feedback", response_model=FeedbackAnalysisResponse)
async def analyze_interview_feedback_endpoint(
    interview_id: int,
    request: AnalyzeFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_interviewer_or_above)
):
    """
    Analyze interview feedback using AI to extract insights and recommendations.
    
    This endpoint uses OpenAI to analyze interview notes and provide:
    - Key strengths demonstrated by the candidate
    - Areas of concern or weaknesses
    - Hiring recommendation (hire/maybe/no-hire)
    - Confidence score for the recommendation
    - Suggested next steps
    
    **Example Request:**
    ```json
    {
      "interview_notes": "Candidate showed strong Python skills and good problem-solving ability. 
                          However, communication could be clearer. Cultural fit seems good."
    }
    ```
    
    **Returns:**
    - Structured analysis with strengths, weaknesses, and recommendation
    - Confidence score (0-100)
    - Skills ratings (1-5 scale)
    """
    logger.info(f"Analyzing feedback for interview {interview_id}")
    
    try:
        # Fetch interview
        interview = crud.get_interview(db=db, interview_id=interview_id)
        if not interview:
            logger.warning(f"Interview not found: {interview_id}")
            raise HTTPException(status_code=404, detail=f"Interview with ID {interview_id} not found")
        
        # Fetch candidate
        candidate = crud.get_candidate(db=db, candidate_id=interview.candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Fetch job (if available)
        job_title = "Position"
        job_description = None
        if interview.job_id:
            job = crud.get_job(db=db, job_id=interview.job_id)
            if job:
                job_title = job.title
                job_description = job.description
        
        # Get candidate resume
        resume_text = candidate.resume_text
        
        # Analyze feedback
        analysis = ai_feedback.analyze_interview_feedback(
            interview_notes=request.interview_notes,
            candidate_name=candidate.name,
            job_title=job_title,
            candidate_resume=resume_text,
            job_description=job_description
        )
        
        # Update interview notes in database
        interview.notes = request.interview_notes
        db.commit()
        
        # Build response
        response = FeedbackAnalysisResponse(
            interview_id=interview.id,
            candidate_name=analysis["candidate_name"],
            job_title=analysis["job_title"],
            strengths=analysis["strengths"],
            weaknesses=analysis["weaknesses"],
            recommendation=analysis["recommendation"],
            confidence_score=analysis["confidence_score"],
            reasoning=analysis["reasoning"],
            next_steps=analysis["next_steps"],
            overall_assessment=analysis["overall_assessment"],
            technical_skills_rating=analysis.get("technical_skills_rating"),
            communication_skills_rating=analysis.get("communication_skills_rating"),
            culture_fit_rating=analysis.get("culture_fit_rating"),
            model_used=analysis["model_used"]
        )
        
        logger.info(f"Analysis complete: {analysis['recommendation']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing interview feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze feedback: {str(e)}")


# ============================================
# Resume Optimizer Models
# ============================================

class ScoreBreakdown(BaseModel):
    """Individual score breakdown for ATS analysis"""
    keyword_optimization: int = Field(..., ge=0, le=100)
    formatting: int = Field(..., ge=0, le=100)
    structure: int = Field(..., ge=0, le=100)
    completeness: int = Field(..., ge=0, le=100)
    relevance: int = Field(..., ge=0, le=100)


class KeywordRecommendation(BaseModel):
    """Recommended keyword with context"""
    keyword: str
    category: str
    priority: str  # "high", "medium", "low"
    reason: str
    context: Optional[str] = None


class ImprovementSuggestion(BaseModel):
    """Actionable improvement suggestion"""
    suggestion: str
    impact: str  # "high", "medium", "low"
    priority: int = Field(..., ge=1, le=5)
    category: str


class SectionRecommendation(BaseModel):
    """Recommendation for resume section"""
    section: str
    recommendation: str
    priority: str


class OptimizeResumeResponse(BaseModel):
    """Response for resume optimization"""
    ats_score: int = Field(..., ge=0, le=100)
    score_breakdown: ScoreBreakdown
    missing_keywords: List[str]
    recommended_keywords: List[KeywordRecommendation]
    formatting_issues: List[str]
    improvement_suggestions: List[ImprovementSuggestion]
    strengths: List[str]
    section_recommendations: List[SectionRecommendation]
    overall_feedback: str
    model_used: str


# ============================================
# Resume Optimizer Endpoints
# ============================================

@router.post("/candidates/{candidate_id}/optimize-resume", response_model=OptimizeResumeResponse)
async def optimize_resume(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Analyze candidate's resume for ATS compatibility and provide improvement suggestions.
    
    Args:
        candidate_id: ID of the candidate
        db: Database session
        
    Returns:
        Comprehensive resume optimization analysis
    """
    logger.info(f"Optimizing resume for candidate ID: {candidate_id}")
    
    try:
        # Fetch candidate
        candidate = crud.get_candidate(db, candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check if resume data exists
        if not candidate.resume_text and not candidate.parsed_json:
            raise HTTPException(status_code=400, detail="No resume data available for this candidate")
        
        # Get resume text - prefer resume_text, fallback to parsed_json
        resume_text = ""
        
        if candidate.resume_text:
            resume_text = candidate.resume_text
        elif candidate.parsed_json:
            try:
                import json
                if isinstance(candidate.parsed_json, str):
                    parsed_data = json.loads(candidate.parsed_json)
                else:
                    parsed_data = candidate.parsed_json
                
                # Extract text from parsed data
                resume_text = f"""
Name: {parsed_data.get('name', 'N/A')}
Email: {parsed_data.get('email', 'N/A')}
Phone: {parsed_data.get('phone', 'N/A')}

Skills: {', '.join(parsed_data.get('skills', []))}

Experience:
{parsed_data.get('experience', 'N/A')}

Education:
{parsed_data.get('education', 'N/A')}
                """.strip()
            except Exception as e:
                logger.warning(f"Could not parse resume JSON: {e}")
                resume_text = str(candidate.parsed_json)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract resume text")
        
        # Perform ATS analysis
        logger.info("Performing ATS analysis...")
        analysis = resume_optimizer.analyze_resume_for_ats(
            resume_text=resume_text,
            candidate_name=candidate.name
        )
        
        # Build response
        response = OptimizeResumeResponse(
            ats_score=analysis["ats_score"],
            score_breakdown=ScoreBreakdown(**analysis["score_breakdown"]),
            missing_keywords=analysis["missing_keywords"],
            recommended_keywords=[
                KeywordRecommendation(**kw) for kw in analysis["recommended_keywords"]
            ],
            formatting_issues=analysis["formatting_issues"],
            improvement_suggestions=[
                ImprovementSuggestion(**suggestion) for suggestion in analysis["improvement_suggestions"]
            ],
            strengths=analysis["strengths"],
            section_recommendations=[
                SectionRecommendation(**rec) for rec in analysis["section_recommendations"]
            ],
            overall_feedback=analysis["overall_feedback"],
            model_used=analysis["model_used"]
        )
        
        logger.info(f"Optimization complete. ATS Score: {analysis['ats_score']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to optimize resume: {str(e)}")

