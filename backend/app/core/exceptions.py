# backend/app/core/exceptions.py
"""
Custom exceptions for the AI Recruit Assistant application.
"""
from fastapi import HTTPException, status


class CandidateNotFoundException(HTTPException):
    """Raised when a candidate is not found."""
    def __init__(self, candidate_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found"
        )


class JobNotFoundException(HTTPException):
    """Raised when a job is not found."""
    def __init__(self, job_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )


class InterviewNotFoundException(HTTPException):
    """Raised when an interview is not found."""
    def __init__(self, interview_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )


class InvalidFileTypeException(HTTPException):
    """Raised when an uploaded file has an invalid type."""
    def __init__(self, filename: str, allowed_types: list):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for '{filename}'. Allowed types: {', '.join(allowed_types)}"
        )


class FileTooLargeException(HTTPException):
    """Raised when an uploaded file exceeds the size limit."""
    def __init__(self, filename: str, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File '{filename}' exceeds maximum size of {max_size_mb}MB"
        )


class ResumeParsingException(HTTPException):
    """Raised when resume parsing fails."""
    def __init__(self, filename: str, reason: str = "Unknown error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume '{filename}': {reason}"
        )


class DatabaseException(HTTPException):
    """Raised when a database operation fails."""
    def __init__(self, operation: str, reason: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation '{operation}' failed: {reason}"
        )


class AIServiceException(HTTPException):
    """Raised when AI service (OpenAI) fails."""
    def __init__(self, service: str = "AI service", reason: str = "Service unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} error: {reason}"
        )


class InvalidScheduleException(HTTPException):
    """Raised when interview scheduling has invalid dates/times."""
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interview schedule: {reason}"
        )
