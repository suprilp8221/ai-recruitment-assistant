# backend/app/services/resume_optimizer.py
"""
AI-powered resume optimization service.
Analyzes resumes and provides improvement suggestions for ATS compatibility.
"""
import os
import json
from openai import OpenAI
from typing import Dict, List, Optional
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_resume_for_ats(
    resume_text: str,
    candidate_name: str,
    target_job_title: Optional[str] = None,
    job_description: Optional[str] = None
) -> Dict:
    """
    Analyze resume for ATS compatibility and provide improvement suggestions.
    
    Args:
        resume_text: The candidate's resume text
        candidate_name: Name of the candidate
        target_job_title: Optional target job title
        job_description: Optional job description for targeted analysis
    
    Returns:
        Dictionary with ATS score, suggestions, keywords, and improvements
    """
    logger.info(f"Analyzing resume for {candidate_name}")
    
    # Build context
    context = f"Candidate: {candidate_name}\n"
    if target_job_title:
        context += f"Target Position: {target_job_title}\n"
    if job_description:
        context += f"\nTarget Job Description:\n{job_description[:800]}\n"
    
    # Build the prompt
    prompt = f"""{context}

Resume Text:
{resume_text[:3000]}

Analyze this resume for ATS (Applicant Tracking System) compatibility and provide comprehensive feedback.

Evaluate the following aspects:

1. **ATS Compatibility Score (0-100)**: Overall score based on:
   - Keyword optimization
   - Formatting clarity
   - Section organization
   - Contact information completeness
   - Relevant skills presence

2. **Missing Keywords**: Important keywords/skills that should be added (based on job description if provided)

3. **Formatting Issues**: Problems that might confuse ATS systems

4. **Improvement Suggestions**: Specific actionable recommendations

5. **Strengths**: What's already good about the resume

6. **Section Recommendations**: Suggestions for organizing/adding sections

Return a JSON object with this exact structure:
{{
  "ats_score": 75,
  "score_breakdown": {{
    "keyword_optimization": 80,
    "formatting": 70,
    "structure": 75,
    "completeness": 80,
    "relevance": 70
  }},
  "missing_keywords": [
    "Python",
    "Machine Learning",
    "AWS"
  ],
  "recommended_keywords": [
    {{
      "keyword": "Python",
      "category": "Technical Skill",
      "priority": "high",
      "reason": "Mentioned in job description"
    }}
  ],
  "formatting_issues": [
    "Use bullet points for better readability",
    "Add clear section headers"
  ],
  "improvement_suggestions": [
    {{
      "category": "Skills",
      "suggestion": "Add a dedicated skills section",
      "impact": "high",
      "priority": 1
    }}
  ],
  "strengths": [
    "Clear work experience",
    "Quantified achievements"
  ],
  "section_recommendations": [
    {{"section": "Summary", "recommendation": "Add a professional summary at the top", "priority": "high"}},
    {{"section": "Skills", "recommendation": "Create a dedicated skills section", "priority": "medium"}}
  ],
  "overall_feedback": "Brief summary of resume quality and main areas to improve"
}}

Return ONLY the JSON object, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume reviewer and ATS specialist. Provide actionable, specific feedback to improve resume quality and ATS compatibility. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1500
        )
        
        # Extract response
        content = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response: {content[:200]}...")
        
        # Parse JSON response
        analysis = json.loads(content)
        
        # Add metadata
        analysis["candidate_name"] = candidate_name
        analysis["target_job_title"] = target_job_title or "General"
        analysis["model_used"] = "gpt-3.5-turbo"
        
        logger.info(f"Analysis complete: ATS score {analysis['ats_score']}/100")
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
        # Fallback: return basic analysis
        return _generate_fallback_analysis(resume_text, candidate_name, target_job_title)
    
    except Exception as e:
        logger.error(f"Error analyzing resume with OpenAI: {str(e)}", exc_info=True)
        # Return fallback analysis
        return _generate_fallback_analysis(resume_text, candidate_name, target_job_title)


def _generate_fallback_analysis(
    resume_text: str,
    candidate_name: str,
    target_job_title: Optional[str] = None
) -> Dict:
    """
    Generate basic resume analysis when OpenAI is not available.
    Uses keyword matching and simple heuristics.
    """
    logger.warning("Using fallback resume analysis")
    
    resume_lower = resume_text.lower()
    word_count = len(resume_text.split())
    
    # Common ATS-friendly keywords
    technical_keywords = [
        'python', 'java', 'javascript', 'react', 'node.js', 'aws', 'docker',
        'kubernetes', 'sql', 'git', 'agile', 'ci/cd', 'api', 'microservices'
    ]
    
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem-solving',
        'project management', 'analytical', 'creative'
    ]
    
    # Check for important sections
    has_summary = any(word in resume_lower for word in ['summary', 'objective', 'profile'])
    has_skills = 'skill' in resume_lower
    has_experience = any(word in resume_lower for word in ['experience', 'employment', 'work history'])
    has_education = 'education' in resume_lower
    has_contact = any(word in resume_lower for word in ['email', '@', 'phone', 'linkedin'])
    
    # Count keyword matches
    tech_matches = sum(1 for kw in technical_keywords if kw in resume_lower)
    soft_matches = sum(1 for kw in soft_skills if kw in resume_lower)
    
    # Calculate score
    base_score = 50
    if has_contact: base_score += 10
    if has_summary: base_score += 5
    if has_skills: base_score += 10
    if has_experience: base_score += 10
    if has_education: base_score += 5
    base_score += min(tech_matches * 2, 10)
    base_score += min(soft_matches * 1, 10)
    
    ats_score = min(base_score, 95)
    
    # Generate suggestions
    missing_sections = []
    if not has_summary:
        missing_sections.append("Professional summary or objective")
    if not has_skills:
        missing_sections.append("Dedicated skills section")
    
    return {
        "candidate_name": candidate_name,
        "target_job_title": target_job_title or "General",
        "ats_score": ats_score,
        "score_breakdown": {
            "keyword_optimization": min(tech_matches * 10, 80),
            "formatting": 70,
            "structure": 75 if has_experience else 50,
            "completeness": 80 if has_contact else 60,
            "relevance": 65
        },
        "missing_keywords": [
            kw for kw in technical_keywords[:5] if kw not in resume_lower
        ],
        "recommended_keywords": [
            {
                "keyword": kw,
                "category": "Technical Skill",
                "priority": "medium",
                "reason": "Common industry requirement"
            } for kw in technical_keywords[:3] if kw not in resume_lower
        ],
        "formatting_issues": [
            "Ensure consistent formatting throughout",
            "Use standard section headers",
            "Keep formatting simple for ATS compatibility"
        ],
        "improvement_suggestions": [
            {
                "category": "Structure",
                "suggestion": section,
                "impact": "high",
                "priority": 1
            } for section in missing_sections
        ] + [
            {
                "category": "Content",
                "suggestion": "Add quantifiable achievements to experience",
                "impact": "medium",
                "priority": 2
            }
        ],
        "strengths": [
            f"Resume length is appropriate ({word_count} words)",
            "Contains relevant keywords"
        ] if tech_matches > 0 else ["Resume structure detected"],
        "section_recommendations": [
            {"section": section, "recommendation": f"Add {section} section to improve ATS compatibility", "priority": "high"}
            for section in missing_sections
        ] if missing_sections else [
            {"section": "Experience", "recommendation": "Consider adding measurable achievements", "priority": "medium"},
            {"section": "Contact", "recommendation": "Update contact information", "priority": "low"}
        ],
        "overall_feedback": f"Resume has a baseline ATS score of {ats_score}/100. Focus on adding missing sections and relevant keywords to improve compatibility with applicant tracking systems.",
        "model_used": "fallback"
    }


def generate_keyword_suggestions(
    job_description: str,
    current_resume: str
) -> List[Dict]:
    """
    Extract important keywords from job description that are missing in resume.
    
    Args:
        job_description: The target job description
        current_resume: Current resume text
    
    Returns:
        List of keyword suggestions with priority and category
    """
    logger.info("Generating keyword suggestions from job description")
    
    prompt = f"""Compare this job description with the candidate's resume and identify missing keywords.

Job Description:
{job_description[:1500]}

Current Resume:
{current_resume[:1500]}

Identify the top 10 most important keywords/skills from the job description that are missing or underrepresented in the resume.

Return JSON array:
[
  {{
    "keyword": "Python",
    "category": "Technical Skill|Soft Skill|Tool|Certification",
    "priority": "high|medium|low",
    "reason": "Why this keyword is important",
    "context": "How it's used in the job description"
  }}
]

Return ONLY the JSON array."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at keyword extraction for ATS optimization. Identify the most important missing keywords."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        keywords = json.loads(content)
        
        logger.info(f"Generated {len(keywords)} keyword suggestions")
        return keywords
        
    except Exception as e:
        logger.error(f"Error generating keywords: {str(e)}", exc_info=True)
        return []
