import os
import sys
import pytest
from fastapi import HTTPException

base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(base_dir)
sys.path.insert(0, backend_dir)

from app.services.matching_service import matching_service


def test_matching_percentage_calculation():
    """
    Validates that match percentage formula:
    round(100.0 * matchCount / requiredSkillCount, 2)
    is correctly applied to all candidate recommendations.
    """
    matches = matching_service.match_jobs_for_candidate("C001")
    assert len(matches) > 0

    for match in matches:
        match_count = match["matchCount"]
        req_count = match["requiredSkillCount"]
        assert req_count > 0
        expected_pct = round(100.0 * match_count / req_count, 2)
        assert match["matchPercentage"] == expected_pct
        assert 0.0 <= match["matchPercentage"] <= 100.0


def test_matching_skill_containment():
    """
    Validates that matching skills returned for a candidate are indeed
    possessed by that candidate.
    """
    candidate_skills = {
        s["name"] for s in matching_service.get_candidate_skills("C001")
    }

    matches = matching_service.match_jobs_for_candidate("C001")
    for match in matches:
        for skill in match["matchingSkills"]:
            assert skill in candidate_skills, f"Skill '{skill}' was matched but candidate C001 does not possess it."


def test_missing_skills_accuracy():
    """
    Validates that missing skills for a job match do NOT intersect with
    the candidate's possessed skills and accurately represent the skill gap.
    """
    candidate_skills = {
        s["name"] for s in matching_service.get_candidate_skills("C001")
    }

    matches = matching_service.match_jobs_for_candidate("C001")
    for match in matches:
        for missing in match["missingSkills"]:
            assert missing not in candidate_skills, f"Skill '{missing}' is marked missing but candidate C001 has it."
            assert missing not in match["matchingSkills"], f"Skill '{missing}' is both matched and missing."


def test_ranking_order():
    """
    Validates that returned jobs are sorted in descending order of match percentage.
    """
    matches = matching_service.match_jobs_for_candidate("C001")
    percentages = [m["matchPercentage"] for m in matches]
    for i in range(len(percentages) - 1):
        assert percentages[i] >= percentages[i + 1]


def test_empty_candidate_id_raises_http_400():
    """
    Validates that passing an empty string or whitespace candidate ID raises HTTP 400.
    """
    with pytest.raises(HTTPException) as exc_info:
        matching_service.match_jobs_for_candidate("")
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info2:
        matching_service.match_jobs_for_candidate("   ")
    assert exc_info2.value.status_code == 400
