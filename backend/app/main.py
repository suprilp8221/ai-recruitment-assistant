# backend/app/main.py
import os
from fastapi import FastAPI, APIRouter, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

# load .env
load_dotenv()

from app.db.database import engine
from app.db import models  # ensure models are imported so metadata exists
from app.api.v1 import health as health_router_module
from app.api.v1 import candidates as candidates_router_module
from app.api.v1 import jobs as jobs_router_module
from app.api.v1 import ranking as ranking_router_module
from app.api.v1 import interviews as interviews_router_module
from app.api.v1 import ai_tools as ai_tools_router_module
from app.api.v1 import auth as auth_router_module
from app.core.logging_config import setup_logging, get_logger

# Initialize logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# create all tables (development helper)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Recruitment Assistant",
    description="AI-powered recruitment platform with resume parsing, candidate ranking, and interview management",
    version="1.0.0"
)

# CORS - Must be added BEFORE other middleware
# Allow all origins for development (file:// and http://localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Starting AI Recruitment Assistant API")

# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Global exception handler for uncaught exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )

# mount simple v1 router
v1 = APIRouter(prefix="/api/v1")
v1.include_router(health_router_module.router, prefix="")
v1.include_router(auth_router_module.router, prefix="/auth", tags=["Authentication"])
v1.include_router(candidates_router_module.router, prefix="")
v1.include_router(jobs_router_module.router, prefix="")
v1.include_router(ranking_router_module.router, prefix="")
v1.include_router(interviews_router_module.router, prefix="")
v1.include_router(ai_tools_router_module.router, prefix="/ai")

app.include_router(v1)
