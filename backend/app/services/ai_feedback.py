# backend/app/services/ai_feedback.py
"""
AI-powered interview feedback analysis service.
Analyzes interview notes to extract insights and hiring recommendations.
"""
import os
import json
from openai import OpenAI
from typing import Dict, Optional
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_interview_feedback(
    interview_notes: str,
    candidate_name: str,
    job_title: str,
    candidate_resume: Optional[str] = None,
    job_description: Optional[str] = None
) -> Dict:
    """
    Analyze interview feedback using OpenAI to extract insights.
    
    Args:
        interview_notes: Raw notes from the interview
        candidate_name: Name of the candidate
        job_title: Job title/position
        candidate_resume: Optional resume text for context
        job_description: Optional job description for context
    
    Returns:
        Dictionary with analysis results including strengths, weaknesses, 
        recommendation, confidence score, and reasoning
    """
    logger.info(f"Analyzing interview feedback for {candidate_name} - {job_title}")
    
    # Build context
    context = f"Job Title: {job_title}\nCandidate: {candidate_name}\n"
    
    if job_description:
        context += f"\nJob Requirements:\n{job_description[:500]}\n"
    
    if candidate_resume:
        context += f"\nCandidate Background:\n{candidate_resume[:500]}\n"
    
    # Build the prompt
    prompt = f"""{context}

Interview Notes/Feedback:
{interview_notes}

Analyze the interview feedback above and provide a comprehensive assessment. Extract:

1. **Key Strengths**: Specific positive attributes, skills, or behaviors demonstrated
2. **Areas of Concern/Weaknesses**: Gaps, red flags, or areas needing improvement
3. **Hiring Recommendation**: Should we hire, maybe/conditional hire, or not hire?
4. **Confidence Level**: How confident are you in this recommendation? (0-100%)
5. **Reasoning**: Brief explanation for the recommendation
6. **Next Steps**: Suggested actions (e.g., second interview, technical assessment, hire, reject)

Format your response as JSON with this exact structure:
{{
  "strengths": [
    "strength 1",
    "strength 2",
    "strength 3"
  ],
  "weaknesses": [
    "weakness 1",
    "weakness 2"
  ],
  "recommendation": "hire|maybe|no-hire",
  "confidence_score": 85,
  "reasoning": "Brief explanation of the recommendation",
  "next_steps": [
    "suggested action 1",
    "suggested action 2"
  ],
  "overall_assessment": "One paragraph summary of the candidate",
  "technical_skills_rating": 4,
  "communication_skills_rating": 5,
  "culture_fit_rating": 4
}}

Return ONLY the JSON object, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced hiring manager and HR professional. Analyze interview feedback objectively and provide actionable insights. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1000
        )
        
        # Extract response
        content = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response: {content[:200]}...")
        
        # Parse JSON response
        analysis = json.loads(content)
        
        # Add metadata
        analysis["candidate_name"] = candidate_name
        analysis["job_title"] = job_title
        analysis["model_used"] = "gpt-3.5-turbo"
        
        logger.info(f"Analysis complete: {analysis['recommendation']} (confidence: {analysis.get('confidence_score', 0)}%)")
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
        # Fallback: return basic analysis
        return _generate_fallback_analysis(interview_notes, candidate_name, job_title)
    
    except Exception as e:
        logger.error(f"Error analyzing feedback with OpenAI: {str(e)}", exc_info=True)
        # Return fallback analysis
        return _generate_fallback_analysis(interview_notes, candidate_name, job_title)


def _generate_fallback_analysis(
    interview_notes: str,
    candidate_name: str,
    job_title: str
) -> Dict:
    """
    Generate basic analysis when OpenAI is not available.
    Uses simple keyword matching and sentiment analysis.
    """
    logger.warning("Using fallback feedback analysis")
    
    notes_lower = interview_notes.lower()
    
    # Simple keyword-based analysis
    positive_keywords = [
        'excellent', 'great', 'strong', 'impressive', 'skilled',
        'knowledgeable', 'experienced', 'professional', 'confident',
        'good communication', 'team player', 'problem solver'
    ]
    
    negative_keywords = [
        'weak', 'lacking', 'inexperienced', 'poor', 'struggled',
        'unclear', 'unprepared', 'not suitable', 'concerns', 'red flag'
    ]
    
    positive_count = sum(1 for kw in positive_keywords if kw in notes_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in notes_lower)
    
    # Determine recommendation
    if positive_count > negative_count + 2:
        recommendation = "hire"
        confidence = min(75 + (positive_count * 5), 95)
    elif negative_count > positive_count + 2:
        recommendation = "no-hire"
        confidence = min(70 + (negative_count * 5), 90)
    else:
        recommendation = "maybe"
        confidence = 60
    
    return {
        "candidate_name": candidate_name,
        "job_title": job_title,
        "strengths": [
            "Positive indicators found in interview feedback",
            "Candidate showed engagement during interview"
        ] if positive_count > 0 else ["Limited positive feedback available"],
        "weaknesses": [
            "Some concerns noted in feedback",
            "Further evaluation may be needed"
        ] if negative_count > 0 else ["No major concerns identified"],
        "recommendation": recommendation,
        "confidence_score": confidence,
        "reasoning": f"Based on keyword analysis of interview notes. Found {positive_count} positive and {negative_count} negative indicators.",
        "next_steps": [
            "Review detailed interview notes",
            "Consider second interview" if recommendation == "maybe" else "Proceed with hiring process" if recommendation == "hire" else "Send rejection notice"
        ],
        "overall_assessment": f"Analysis based on available interview notes for {candidate_name} applying for {job_title}. AI-powered analysis unavailable.",
        "technical_skills_rating": 3,
        "communication_skills_rating": 3,
        "culture_fit_rating": 3,
        "model_used": "fallback"
    }


def summarize_multiple_interviews(
    interview_feedbacks: list,
    candidate_name: str,
    job_title: str
) -> Dict:
    """
    Analyze feedback from multiple interview rounds.
    
    Args:
        interview_feedbacks: List of interview note strings
        candidate_name: Name of the candidate
        job_title: Job title
    
    Returns:
        Consolidated analysis across all interviews
    """
    logger.info(f"Analyzing {len(interview_feedbacks)} interview rounds for {candidate_name}")
    
    # Combine all feedback
    combined_notes = "\n\n=== Interview Round Separator ===\n\n".join(interview_feedbacks)
    
    prompt = f"""Analyze feedback from {len(interview_feedbacks)} interview rounds for {candidate_name} applying for {job_title}.

Combined Interview Feedback:
{combined_notes[:2000]}

Provide a consolidated analysis across all interview rounds. Look for:
1. Consistent strengths mentioned across interviews
2. Recurring concerns or weaknesses
3. Evolution of candidate performance across rounds
4. Overall hiring recommendation considering all feedback

Return JSON with the same structure as single interview analysis."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced hiring manager analyzing multiple interview rounds. Provide consolidated insights."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        
        content = response.choices[0].message.content.strip()
        analysis = json.loads(content)
        
        analysis["candidate_name"] = candidate_name
        analysis["job_title"] = job_title
        analysis["interview_rounds_analyzed"] = len(interview_feedbacks)
        analysis["model_used"] = "gpt-3.5-turbo"
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in multi-interview analysis: {str(e)}", exc_info=True)
        # Fall back to analyzing just the most recent interview
        return analyze_interview_feedback(
            interview_feedbacks[-1] if interview_feedbacks else "",
            candidate_name,
            job_title
        )
