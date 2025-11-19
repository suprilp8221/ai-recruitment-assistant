# backend/app/services/interview_questions.py
"""
AI-powered interview question generator service.
Generates personalized interview questions based on job requirements and candidate profile.
"""
import os
import json
from openai import OpenAI
from typing import List, Dict, Optional
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_interview_questions(
    job_description: str,
    candidate_resume: str,
    candidate_skills: List[str],
    experience_level: str = "mid",
    question_count: int = 10,
    question_types: Optional[List[str]] = None
) -> Dict:
    """
    Generate personalized interview questions using OpenAI.
    
    Args:
        job_description: Job requirements and description
        candidate_resume: Candidate's resume text
        candidate_skills: List of candidate's skills
        experience_level: junior, mid, or senior
        question_count: Number of questions to generate
        question_types: List of types (technical, behavioral, situational, culture-fit)
    
    Returns:
        Dictionary with categorized questions
    """
    if question_types is None:
        question_types = ["technical", "behavioral"]
    
    logger.info(f"Generating {question_count} interview questions for {experience_level} level")
    
    # Build the prompt
    prompt = f"""You are an expert technical recruiter. Generate {question_count} interview questions for a candidate.

Job Description:
{job_description}

Candidate Skills: {', '.join(candidate_skills) if candidate_skills else 'Not specified'}
Experience Level: {experience_level}
Question Types Needed: {', '.join(question_types)}

Candidate Resume Summary:
{candidate_resume[:1500]}  # Limit resume text to avoid token limit

Generate exactly {question_count} interview questions that:
1. Are relevant to the job requirements
2. Match the candidate's experience level
3. Include a mix of: {', '.join(question_types)}
4. Test both technical skills and problem-solving ability
5. Are specific and actionable (not generic)

Format your response as a JSON array with this structure:
[
  {{
    "question": "The interview question text",
    "type": "technical|behavioral|situational|culture-fit",
    "difficulty": "easy|medium|hard",
    "category": "specific skill or topic",
    "follow_up": "optional follow-up question"
  }}
]

Return ONLY the JSON array, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter who generates insightful interview questions. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract response
        content = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response: {content[:200]}...")
        
        # Parse JSON response
        questions = json.loads(content)
        
        # Categorize questions
        categorized = {
            "technical": [],
            "behavioral": [],
            "situational": [],
            "culture_fit": []
        }
        
        for q in questions:
            q_type = q.get("type", "technical").lower().replace("-", "_")
            if q_type in categorized:
                categorized[q_type].append(q)
            else:
                categorized["technical"].append(q)
        
        result = {
            "total_questions": len(questions),
            "questions": questions,
            "categorized": categorized,
            "experience_level": experience_level,
            "model_used": "gpt-3.5-turbo"
        }
        
        logger.info(f"Successfully generated {len(questions)} questions")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
        # Fallback: return generic questions
        return _generate_fallback_questions(question_count, experience_level)
    
    except Exception as e:
        logger.error(f"Error generating questions with OpenAI: {str(e)}", exc_info=True)
        # Return fallback questions
        return _generate_fallback_questions(question_count, experience_level)


def _generate_fallback_questions(count: int, level: str) -> Dict:
    """
    Generate fallback questions when OpenAI fails.
    """
    logger.warning("Using fallback question generation")
    
    fallback_questions = {
        "junior": [
            {
                "question": "Tell me about a challenging project you worked on and how you approached it.",
                "type": "behavioral",
                "difficulty": "easy",
                "category": "Problem Solving"
            },
            {
                "question": "How do you stay updated with new technologies and best practices?",
                "type": "behavioral",
                "difficulty": "easy",
                "category": "Learning & Development"
            },
            {
                "question": "Describe a time when you had to debug a difficult issue. What was your approach?",
                "type": "technical",
                "difficulty": "medium",
                "category": "Debugging"
            },
            {
                "question": "How do you handle working on multiple tasks with tight deadlines?",
                "type": "behavioral",
                "difficulty": "easy",
                "category": "Time Management"
            },
            {
                "question": "What interests you most about this role and our company?",
                "type": "culture_fit",
                "difficulty": "easy",
                "category": "Motivation"
            }
        ],
        "mid": [
            {
                "question": "Describe your experience with design patterns. Which ones do you use most frequently?",
                "type": "technical",
                "difficulty": "medium",
                "category": "Architecture"
            },
            {
                "question": "Tell me about a time you had to make a technical trade-off decision.",
                "type": "behavioral",
                "difficulty": "medium",
                "category": "Decision Making"
            },
            {
                "question": "How do you approach code reviews? What do you look for?",
                "type": "technical",
                "difficulty": "medium",
                "category": "Code Quality"
            },
            {
                "question": "Describe a situation where you had to mentor a junior developer.",
                "type": "behavioral",
                "difficulty": "medium",
                "category": "Leadership"
            },
            {
                "question": "How do you balance technical debt with feature development?",
                "type": "situational",
                "difficulty": "medium",
                "category": "Project Management"
            }
        ],
        "senior": [
            {
                "question": "How do you approach system design for high-scale applications?",
                "type": "technical",
                "difficulty": "hard",
                "category": "System Design"
            },
            {
                "question": "Describe a situation where you influenced the technical direction of a project.",
                "type": "behavioral",
                "difficulty": "hard",
                "category": "Leadership"
            },
            {
                "question": "How do you evaluate and introduce new technologies to a team?",
                "type": "situational",
                "difficulty": "hard",
                "category": "Technology Leadership"
            },
            {
                "question": "Tell me about a time you had to resolve a conflict between team members.",
                "type": "behavioral",
                "difficulty": "hard",
                "category": "Conflict Resolution"
            },
            {
                "question": "How do you ensure code quality and maintainability in a large codebase?",
                "type": "technical",
                "difficulty": "hard",
                "category": "Code Quality"
            }
        ]
    }
    
    questions = fallback_questions.get(level, fallback_questions["mid"])[:count]
    
    categorized = {
        "technical": [q for q in questions if q["type"] == "technical"],
        "behavioral": [q for q in questions if q["type"] == "behavioral"],
        "situational": [q for q in questions if q["type"] == "situational"],
        "culture_fit": [q for q in questions if q["type"] == "culture_fit"]
    }
    
    return {
        "total_questions": len(questions),
        "questions": questions,
        "categorized": categorized,
        "experience_level": level,
        "model_used": "fallback"
    }


def generate_questions_for_candidate_job(
    candidate_name: str,
    job_title: str,
    job_description: str,
    resume_text: str,
    skills: List[str],
    experience_level: str = "mid",
    count: int = 10
) -> Dict:
    """
    Convenience wrapper to generate questions with candidate and job info.
    
    Args:
        candidate_name: Name of the candidate
        job_title: Job title
        job_description: Full job description
        resume_text: Candidate's resume text
        skills: Candidate's skills
        experience_level: Experience level
        count: Number of questions
    
    Returns:
        Dictionary with questions and metadata
    """
    result = generate_interview_questions(
        job_description=job_description,
        candidate_resume=resume_text,
        candidate_skills=skills,
        experience_level=experience_level,
        question_count=count
    )
    
    # Add metadata
    result["candidate_name"] = candidate_name
    result["job_title"] = job_title
    
    return result
