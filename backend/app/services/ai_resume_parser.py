# backend/app/services/ai_resume_parser.py
"""
AI-powered resume parser using OpenAI for structured data extraction.
Extracts skills, experience, education, and contact information from resume text.
"""
import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment (.env)")

client = OpenAI(api_key=OPENAI_KEY)
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def parse_resume_with_ai(resume_text: str) -> Optional[Dict[str, Any]]:
    """
    Use OpenAI to extract structured information from resume text.
    
    Args:
        resume_text: Raw text extracted from PDF/DOCX
        
    Returns:
        Dictionary with structured resume data or None if parsing fails
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return None
    
    # Truncate very long resumes to save tokens
    max_chars = 6000
    if len(resume_text) > max_chars:
        resume_text = resume_text[:max_chars] + "\n...[truncated]"
    
    prompt = _build_parsing_prompt(resume_text)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume parser. Extract structured information from resumes and return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=1500,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks or other formatting
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(content[start:end])
            else:
                return None
        
        # Validate and normalize the response
        return _normalize_parsed_data(parsed)
        
    except Exception as e:
        print(f"AI resume parsing error: {e}")
        return None


def _build_parsing_prompt(resume_text: str) -> str:
    """Build the prompt for AI resume parsing."""
    return f"""Extract structured information from the following resume and return ONLY valid JSON with this exact structure:

{{
  "contact": {{
    "name": "string or null",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string or null",
    "github": "string or null",
    "portfolio": "string or null"
  }},
  "summary": "brief professional summary (2-3 sentences) or null",
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "location": "city, state/country or null",
      "start_date": "YYYY-MM or YYYY or null",
      "end_date": "YYYY-MM or YYYY or 'Present' or null",
      "duration": "X years Y months or null",
      "responsibilities": ["responsibility1", "responsibility2", ...]
    }}
  ],
  "education": [
    {{
      "degree": "degree name",
      "institution": "school/university name",
      "location": "city, state/country or null",
      "graduation_date": "YYYY or YYYY-MM or null",
      "gpa": "X.XX or null",
      "field_of_study": "major/field or null"
    }}
  ],
  "certifications": ["cert1", "cert2", ...],
  "languages": ["language1", "language2", ...],
  "projects": [
    {{
      "name": "project name",
      "description": "brief description",
      "technologies": ["tech1", "tech2", ...],
      "url": "project url or null"
    }}
  ]
}}

Resume text:
\"\"\"
{resume_text}
\"\"\"

Return ONLY the JSON, no additional text or explanation."""


def _normalize_parsed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate parsed resume data.
    Ensures all required fields exist with proper defaults.
    """
    normalized = {
        "contact": data.get("contact", {}),
        "summary": data.get("summary") or "",
        "skills": data.get("skills", []),
        "experience": data.get("experience", []),
        "education": data.get("education", []),
        "certifications": data.get("certifications", []),
        "languages": data.get("languages", []),
        "projects": data.get("projects", [])
    }
    
    # Ensure contact is a dict
    if not isinstance(normalized["contact"], dict):
        normalized["contact"] = {}
    
    # Ensure lists are actually lists
    for key in ["skills", "experience", "education", "certifications", "languages", "projects"]:
        if not isinstance(normalized[key], list):
            normalized[key] = []
    
    # Limit array sizes to prevent database bloat
    normalized["skills"] = normalized["skills"][:50]
    normalized["experience"] = normalized["experience"][:20]
    normalized["education"] = normalized["education"][:10]
    normalized["certifications"] = normalized["certifications"][:20]
    normalized["languages"] = normalized["languages"][:10]
    normalized["projects"] = normalized["projects"][:15]
    
    # Truncate summary if too long
    if len(normalized["summary"]) > 1000:
        normalized["summary"] = normalized["summary"][:997] + "..."
    
    return normalized


def extract_contact_info(parsed_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Extract contact information from parsed resume data.
    
    Returns:
        Dict with email, phone, and name if available
    """
    contact = parsed_data.get("contact", {})
    return {
        "name": contact.get("name"),
        "email": contact.get("email"),
        "phone": contact.get("phone")
    }


def get_skills_list(parsed_data: Dict[str, Any]) -> list:
    """Extract flat list of skills from parsed data."""
    return parsed_data.get("skills", [])


def get_experience_summary(parsed_data: Dict[str, Any]) -> str:
    """Generate a text summary of work experience."""
    experiences = parsed_data.get("experience", [])
    if not experiences:
        return "No work experience listed"
    
    summary_parts = []
    for exp in experiences[:5]:  # Limit to 5 most recent
        title = exp.get("title", "Unknown")
        company = exp.get("company", "Unknown Company")
        duration = exp.get("duration", "")
        summary_parts.append(f"{title} at {company}" + (f" ({duration})" if duration else ""))
    
    return " | ".join(summary_parts)
