# backend/app/api/v1/auth.py
"""
Authentication endpoints for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta

from app.db.database import get_db
from app.db import models
from app.services import auth
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)
security = HTTPBearer()


# ============================================
# Request/Response Models
# ============================================

class UserRegisterRequest(BaseModel):
    """Request model for user registration"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = Field(default="recruiter", pattern="^(admin|recruiter|interviewer)$")


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Response model for user data"""
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


# ============================================
# Authentication Endpoints
# ============================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Access token and user information
    """
    logger.info(f"Registering new user: {user_data.email}")
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Registration failed: Email already exists - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = auth.hash_password(user_data.password)
    
    # Create new user
    new_user = models.User(
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User created successfully: {new_user.id} - {new_user.email}")
    
    # Generate access token
    access_token = auth.create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "is_active": new_user.is_active
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and generate access token.
    
    Args:
        credentials: User login credentials
        db: Database session
        
    Returns:
        Access token and user information
    """
    logger.info(f"Login attempt for: {credentials.email}")
    
    # Find user by email
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    
    if not user:
        logger.warning(f"Login failed: User not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not auth.verify_password(credentials.password, user.password_hash):
        logger.warning(f"Login failed: Invalid password - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: Account inactive - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    logger.info(f"Login successful: {user.email}")
    
    # Generate access token
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        Current user information
    """
    token = credentials.credentials
    payload = auth.decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )
