# ==============================================================================
# Cypher Queries for Candidate-Job Skill Matching Application
# All queries are parameterized ($candidateId, $jobId, etc.) for safety & performance.
# ==============================================================================

GET_ALL_CANDIDATES = """
MATCH (c:Candidate)
OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill)
RETURN
    c.id AS id,
    c.name AS name,
    c.yearsExperience AS yearsExperience,
    c.email AS email,
    collect(DISTINCT s.name) AS skills
ORDER BY c.id
"""


GET_CANDIDATE = """
MATCH (c:Candidate {id: $candidateId})
OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill)
OPTIONAL MATCH (c)-[:WORKED_AT]->(co:Company)
RETURN
    c.id AS id,
    c.name AS name,
    c.yearsExperience AS yearsExperience,
    c.email AS email,
    collect(DISTINCT s.name) AS skills,
    collect(DISTINCT co.name) AS previousCompanies
"""


CHECK_CANDIDATE_EXISTS = """
MATCH (c:Candidate {id: $candidateId})
RETURN count(c) > 0 AS exists
"""


GET_CANDIDATE_SKILLS = """
MATCH (c:Candidate {id: $candidateId})-[:HAS_SKILL]->(s:Skill)
RETURN
    s.id AS id,
    s.name AS name,
    s.category AS category
ORDER BY s.name
"""


GET_ALL_JOBS = """
MATCH (j:Job)
OPTIONAL MATCH (j)-[:REQUIRES]->(s:Skill)
OPTIONAL MATCH (co:Company)-[:OFFERS]->(j)
RETURN
    j.id AS id,
    j.title AS title,
    j.location AS location,
    j.type AS type,
    j.minExperience AS minExperience,
    co.name AS company,
    collect(DISTINCT s.name) AS requiredSkills
ORDER BY j.id
"""


GET_JOB_BY_ID = """
MATCH (j:Job {id: $jobId})
OPTIONAL MATCH (j)-[:REQUIRES]->(s:Skill)
OPTIONAL MATCH (co:Company)-[:OFFERS]->(j)
RETURN
    j.id AS id,
    j.title AS title,
    j.location AS location,
    j.type AS type,
    j.minExperience AS minExperience,
    co.name AS company,
    collect(DISTINCT s.name) AS requiredSkills
"""


GET_JOB_SKILLS = """
MATCH (j:Job {id: $jobId})-[:REQUIRES]->(s:Skill)
RETURN
    s.id AS id,
    s.name AS name,
    s.category AS category
ORDER BY s.name
"""


GET_JOB_COMPANY = """
MATCH (c:Company)-[:OFFERS]->(j:Job {id: $jobId})
RETURN
    c.id AS id,
    c.name AS name,
    c.industry AS industry
"""


GET_ALL_SKILLS = """
MATCH (s:Skill)
RETURN
    s.id AS id,
    s.name AS name,
    s.category AS category
ORDER BY s.name
"""


GET_JOB_RECOMMENDATIONS = """
MATCH (c:Candidate {id: $candidateId})
      -[:HAS_SKILL]->(s:Skill)
      <-[:REQUIRES]-(j:Job)

WITH
    j,
    collect(DISTINCT s.name) AS matchingSkills,
    count(DISTINCT s) AS matchCount

MATCH (j)-[:REQUIRES]->(required:Skill)
OPTIONAL MATCH (co:Company)-[:OFFERS]->(j)

WITH
    j,
    co,
    matchingSkills,
    matchCount,
    collect(DISTINCT required.name) AS allRequiredSkills,
    count(DISTINCT required) AS requiredSkillCount

RETURN
    j.id AS jobId,
    j.title AS title,
    j.location AS location,
    j.type AS type,
    co.name AS company,
    matchingSkills,
    matchCount,
    requiredSkillCount,
    [skill IN allRequiredSkills WHERE NOT skill IN matchingSkills] AS missingSkills,
    (100.0 * matchCount / requiredSkillCount) AS matchPercentage

ORDER BY matchPercentage DESC, matchCount DESC, j.title ASC
"""