# backend/app/schemas.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Any, List
from datetime import datetime
from app.core.security import validate_phone_number, validate_string_length


class CandidateCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        validate_string_length(v, "Name", min_length=2, max_length=100)
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not validate_phone_number(v):
            raise ValueError("Invalid phone number format")
        return v


class CandidateOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    parsed_json: Optional[Any] = None
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        validate_string_length(v, "Job title", min_length=3, max_length=200)
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v:
            validate_string_length(v, "Job description", min_length=10, max_length=5000)
            return v.strip()
        return v


class JobOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewCreate(BaseModel):
    candidate_id: int
    job_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    interviewer: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('candidate_id', 'job_id')
    @classmethod
    def validate_ids(cls, v):
        if v is not None and v <= 0:
            raise ValueError("ID must be a positive integer")
        return v
    
    @field_validator('interviewer')
    @classmethod
    def validate_interviewer(cls, v):
        if v:
            validate_string_length(v, "Interviewer name", min_length=2, max_length=100)
            return v.strip()
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v:
            validate_string_length(v, "Notes", min_length=1, max_length=2000)
            return v.strip()
        return v


class InterviewUpdate(BaseModel):
    job_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    interviewer: Optional[str] = None
    notes: Optional[str] = None


class InterviewNotesUpdate(BaseModel):
    notes: str


class InterviewOut(BaseModel):
    id: int
    candidate_id: int
    job_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    interviewer: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

