# backend/app/core/auth_dependencies.py
"""
Authentication dependencies for FastAPI endpoints.
Provides JWT token validation and role-based access control.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.db import models
from app.services import auth
from app.core.logging_config import get_logger

security = HTTPBearer()
logger = get_logger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    token = credentials.credentials
    
    try:
        # Decode and validate the JWT token
        payload = auth.decode_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Fetch user from database
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        logger.debug(f"Authenticated user: {user.email} (role: {user.role})")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Dependency to ensure user is active.
    This is an alias for get_current_user (already checks is_active).
    """
    return current_user


async def require_admin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Dependency to require admin role.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        logger.warning(f"Access denied: User {current_user.email} (role: {current_user.role}) attempted admin action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def require_recruiter_or_admin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Dependency to require recruiter or admin role.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The recruiter or admin user
        
    Raises:
        HTTPException: If user is neither recruiter nor admin
    """
    if current_user.role not in ["admin", "recruiter"]:
        logger.warning(f"Access denied: User {current_user.email} (role: {current_user.role}) attempted recruiter action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter or admin privileges required"
        )
    return current_user


async def require_interviewer_or_above(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Dependency to require interviewer, recruiter, or admin role.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The user with appropriate role
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    if current_user.role not in ["admin", "recruiter", "interviewer"]:
        logger.warning(f"Access denied: User {current_user.email} (role: {current_user.role}) attempted interviewer action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Interviewer, recruiter, or admin privileges required"
        )
    return current_user
