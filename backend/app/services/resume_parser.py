# backend/app/services/resume_parser.py
import os
from typing import Dict, Optional
from pdfminer.high_level import extract_text
import docx
from app.services.ai_resume_parser import parse_resume_with_ai

# Note: This module provides basic text extraction from PDF/DOCX files
# and delegates structured parsing to AI-powered parser


def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from PDF file using pdfminer."""
    try:
        text = extract_text(path)
        return text or ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(path: str) -> str:
    """Extract raw text from DOCX file."""
    try:
        doc = docx.Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""


def parse_resume_text(text: str, use_ai: bool = True) -> Dict:
    """
    Parse resume text into structured format.
    
    Args:
        text: Raw resume text
        use_ai: If True, use AI-powered parsing. If False or AI fails, use basic parsing
        
    Returns:
        Dictionary with structured resume data
    """
    if not text:
        return _get_empty_resume_structure()
    
    # Try AI parsing first if enabled
    if use_ai:
        try:
            ai_result = parse_resume_with_ai(text)
            if ai_result:
                return ai_result
        except Exception as e:
            print(f"AI parsing failed, falling back to basic: {e}")
    
    # Fallback to basic parsing
    return parse_resume_text_basic(text)


def parse_resume_text_basic(text: str) -> Dict:
    """
    Basic fallback parser when AI is unavailable or fails.
    Extracts minimal information without AI.
    
    Args:
        text: Raw resume text
        
    Returns:
        Dictionary with basic parsed data
    """
    if not text:
        return _get_empty_resume_structure()

    # Create basic summary from first portion of text
    summary = text.strip().replace("\r", " ").replace("\n", " ")
    summary = " ".join(summary.split())  # normalize spaces
    if len(summary) > 500:
        summary_short = summary[:500].rsplit(" ", 1)[0] + "..."
    else:
        summary_short = summary

    return {
        "contact": {},
        "summary": summary_short,
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "languages": [],
        "projects": []
    }


def _get_empty_resume_structure() -> Dict:
    """Return empty resume structure."""
    return {
        "contact": {},
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "languages": [],
        "projects": []
    }
