import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(base_dir)
sys.path.insert(0, backend_dir)

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns status online and API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data
    assert data["service"] == "CognoDB Job Recommendation API"


def test_health_check_endpoint():
    """Test database health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["result"] == 1


def test_database_test_endpoint():
    """Test database-test alias endpoint."""
    response = client.get("/database-test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_candidates():
    """Test fetching all candidates."""
    response = client.get("/candidates")
    assert response.status_code == 200
    candidates = response.json()
    assert isinstance(candidates, list)
    assert len(candidates) > 0
    first = candidates[0]
    assert "id" in first
    assert "name" in first
    assert "skills" in first
    assert isinstance(first["skills"], list)


def test_get_candidate_by_id_success():
    """Test fetching single candidate by existing ID."""
    response = client.get("/candidates/C001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "C001"
    assert data["name"] == "John Smith"
    assert "skills" in data
    assert "previousCompanies" in data


def test_get_candidate_by_id_not_found():
    """Test 404 error when candidate does not exist."""
    response = client.get("/candidates/C999999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_candidate_skills():
    """Test fetching candidate skills."""
    response = client.get("/candidates/C001/skills")
    assert response.status_code == 200
    skills = response.json()
    assert isinstance(skills, list)
    assert len(skills) > 0
    skill_names = [s["name"] for s in skills]
    assert "Python" in skill_names


def test_get_candidate_skills_not_found():
    """Test 404 when fetching skills for non-existent candidate."""
    response = client.get("/candidates/C_NON_EXISTENT/skills")
    assert response.status_code == 404


def test_get_jobs():
    """Test fetching all jobs."""
    response = client.get("/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    first = jobs[0]
    assert "id" in first
    assert "title" in first
    assert "location" in first
    assert "requiredSkills" in first


def test_get_job_by_id_success():
    """Test fetching single job by ID."""
    response = client.get("/jobs/J001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "J001"
    assert "Python" in data["title"]
    assert "company" in data


def test_get_job_by_id_not_found():
    """Test 404 error when job does not exist."""
    response = client.get("/jobs/J999999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_skills():
    """Test fetching all skills."""
    response = client.get("/skills")
    assert response.status_code == 200
    skills = response.json()
    assert isinstance(skills, list)
    assert len(skills) >= 6
    skill_names = [s["name"] for s in skills]
    assert "Python" in skill_names
    assert "SQL" in skill_names


def test_matching_endpoint_success():
    """Test matching jobs for candidate C001."""
    response = client.get("/match/C001")
    assert response.status_code == 200
    matches = response.json()
    assert isinstance(matches, list)
    assert len(matches) > 0

    # Verify matching response schema
    first_match = matches[0]
    assert "jobId" in first_match
    assert "title" in first_match
    assert "matchingSkills" in first_match
    assert "matchCount" in first_match
    assert "requiredSkillCount" in first_match
    assert "missingSkills" in first_match
    assert "matchPercentage" in first_match

    # Verify descending sort order
    percentages = [m["matchPercentage"] for m in matches]
    assert percentages == sorted(percentages, reverse=True)


def test_matching_endpoint_candidate_not_found():
    """Test 404 for matching on non-existent candidate."""
    response = client.get("/match/C_NON_EXISTENT")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_matching_alias_endpoint():
    """Test /candidates/{id}/recommendations endpoint produces identical results to /match/{id}."""
    resp1 = client.get("/match/C001")
    resp2 = client.get("/candidates/C001/recommendations")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json() == resp2.json()


def test_cors_headers_present():
    """Test CORS headers are returned in preflight / request."""
    origin = "http://127.0.0.1:5500"
    response = client.get("/", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ["*", origin]
