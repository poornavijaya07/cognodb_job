import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from app.database.connection import get_db_session
from app.queries.job_queries import (
    GET_ALL_CANDIDATES,
    GET_CANDIDATE,
    CHECK_CANDIDATE_EXISTS,
    GET_CANDIDATE_SKILLS,
    GET_ALL_JOBS,
    GET_JOB_BY_ID,
    GET_ALL_SKILLS,
    GET_JOB_RECOMMENDATIONS
)

logger = logging.getLogger("matching_service")


class MatchingService:
    """
    Business logic layer for managing Candidates, Jobs, Skills, and Graph-based Matching.
    """

    @staticmethod
    def get_candidates() -> List[Dict[str, Any]]:
        """Fetch all candidates from the graph database."""
        with get_db_session() as session:
            result = session.run(GET_ALL_CANDIDATES)
            return [record.data() for record in result]

    @staticmethod
    def get_candidate_by_id(candidate_id: str) -> Dict[str, Any]:
        """Fetch a specific candidate by their ID."""
        clean_id = (candidate_id or "").strip()
        if not clean_id:
            raise HTTPException(status_code=400, detail="Candidate ID cannot be empty.")

        with get_db_session() as session:
            result = session.run(GET_CANDIDATE, candidateId=clean_id)
            record = result.single()
            if not record or not record.get("id"):
                raise HTTPException(
                    status_code=404,
                    detail=f"Candidate '{clean_id}' not found."
                )
            return record.data()

    @staticmethod
    def candidate_exists(candidate_id: str) -> bool:
        """Check if candidate exists in graph."""
        clean_id = (candidate_id or "").strip()
        if not clean_id:
            return False

        with get_db_session() as session:
            result = session.run(CHECK_CANDIDATE_EXISTS, candidateId=clean_id)
            record = result.single()
            return bool(record and record.get("exists"))

    @staticmethod
    def get_candidate_skills(candidate_id: str) -> List[Dict[str, Any]]:
        """Fetch skills associated with a specific candidate."""
        clean_id = (candidate_id or "").strip()
        if not clean_id:
            raise HTTPException(status_code=400, detail="Candidate ID cannot be empty.")

        if not MatchingService.candidate_exists(clean_id):
            raise HTTPException(
                status_code=404,
                detail=f"Candidate '{clean_id}' not found."
            )

        with get_db_session() as session:
            result = session.run(GET_CANDIDATE_SKILLS, candidateId=clean_id)
            return [record.data() for record in result]

    @staticmethod
    def get_all_jobs() -> List[Dict[str, Any]]:
        """Fetch all jobs from the graph database."""
        with get_db_session() as session:
            result = session.run(GET_ALL_JOBS)
            return [record.data() for record in result]

    @staticmethod
    def get_job_by_id(job_id: str) -> Dict[str, Any]:
        """Fetch a single job by ID."""
        clean_id = (job_id or "").strip()
        if not clean_id:
            raise HTTPException(status_code=400, detail="Job ID cannot be empty.")

        with get_db_session() as session:
            result = session.run(GET_JOB_BY_ID, jobId=clean_id)
            record = result.single()
            if not record or not record.get("id"):
                raise HTTPException(
                    status_code=404,
                    detail=f"Job '{clean_id}' not found."
                )
            return record.data()

    @staticmethod
    def get_all_skills() -> List[Dict[str, Any]]:
        """Fetch all unique skills in the graph database."""
        with get_db_session() as session:
            result = session.run(GET_ALL_SKILLS)
            return [record.data() for record in result]

    @staticmethod
    def match_jobs_for_candidate(candidate_id: str) -> List[Dict[str, Any]]:
        """
        Execute multi-hop graph traversal to match jobs for candidate based on shared skills.
        Calculates:
        - matchingSkills
        - matchCount
        - requiredSkillCount
        - missingSkills
        - matchPercentage = round(100.0 * matchCount / requiredSkillCount, 2)
        """
        clean_id = (candidate_id or "").strip()
        if not clean_id:
            raise HTTPException(status_code=400, detail="Candidate ID cannot be empty.")

        # Validate existence of candidate to return 404 appropriately
        if not MatchingService.candidate_exists(clean_id):
            raise HTTPException(
                status_code=404,
                detail=f"Candidate '{clean_id}' not found."
            )

        with get_db_session() as session:
            result = session.run(
                GET_JOB_RECOMMENDATIONS,
                candidateId=clean_id
            )
            recommendations = []
            for record in result:
                data = record.data()
                if "matchPercentage" in data and data["matchPercentage"] is not None:
                    data["matchPercentage"] = round(float(data["matchPercentage"]), 2)
                recommendations.append(data)
            return recommendations


matching_service = MatchingService()
