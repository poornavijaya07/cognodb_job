import logging
from typing import List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError

from app.database.connection import test_connection, close_driver
from app.services.matching_service import matching_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cognodb_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting CognoDB Job Recommendation API...")
    yield
    # Shutdown logic
    logger.info("Closing database connections...")
    close_driver()


app = FastAPI(
    title="CognoDB Job Recommendation API",
    description="Intelligent Candidate–Job Skill Matching System powered by CognoDB / Neo4j Graph Database",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local frontend development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Global Exception Handlers (Graceful Error Handling without Credential Leakage)
# ==============================================================================

@app.exception_handler(ServiceUnavailable)
async def service_unavailable_handler(request: Request, exc: ServiceUnavailable):
    logger.error(f"Database Service Unavailable: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "CognoDB/Neo4j database service is currently unavailable. Please check the connection."}
    )


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    logger.error(f"Database Authentication Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database authentication failed. Please verify credentials in the configuration."}
    )


@app.exception_handler(Neo4jError)
async def neo4j_error_handler(request: Request, exc: Neo4jError):
    logger.error(f"Database Query Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred while processing your request."}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."}
    )


# ==============================================================================
# API Routes
# ==============================================================================

@app.get("/", tags=["Health & Info"])
def home():
    """Application health and metadata endpoint."""
    return {
        "status": "online",
        "service": "CognoDB Job Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "database_test": "/database-test",
            "candidates": "/candidates",
            "candidate_detail": "/candidates/{candidate_id}",
            "candidate_skills": "/candidates/{candidate_id}/skills",
            "jobs": "/jobs",
            "skills": "/skills",
            "match": "/match/{candidate_id}",
            "recommendations": "/candidates/{candidate_id}/recommendations"
        }
    }


@app.get("/health", tags=["Health & Info"])
@app.get("/database-test", tags=["Health & Info"])
def database_health_check():
    """Verifies CognoDB / Neo4j database connectivity."""
    try:
        res = test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "result": res
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CognoDB database is not reachable."
        )


@app.get("/candidates", tags=["Candidates"])
def get_candidates():
    """Retrieve all available candidates in the graph database."""
    return matching_service.get_candidates()


@app.get("/candidates/{candidate_id}", tags=["Candidates"])
def get_candidate(candidate_id: str):
    """Retrieve details for a specific candidate by ID."""
    return matching_service.get_candidate_by_id(candidate_id)


@app.get("/candidates/{candidate_id}/skills", tags=["Candidates"])
def get_candidate_skills(candidate_id: str):
    """Retrieve all skills possessed by a specific candidate."""
    return matching_service.get_candidate_skills(candidate_id)


@app.get("/jobs", tags=["Jobs"])
def get_jobs():
    """Retrieve all available jobs with their required skills."""
    return matching_service.get_all_jobs()


@app.get("/jobs/{job_id}", tags=["Jobs"])
def get_job(job_id: str):
    """Retrieve details for a specific job by ID."""
    return matching_service.get_job_by_id(job_id)


@app.get("/skills", tags=["Skills"])
def get_skills():
    """Retrieve all available skills in the database."""
    return matching_service.get_all_skills()


@app.get("/match/{candidate_id}", tags=["Matching"])
@app.get("/candidates/{candidate_id}/recommendations", tags=["Matching"])
def get_job_recommendations(candidate_id: str):
    """
    Find and rank matching jobs for a candidate based on graph traversals.
    Returns match percentage, matching skills, required skills count, and missing skills.
    """
    return matching_service.match_jobs_for_candidate(candidate_id)