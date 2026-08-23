You are the lead developer for my Wexa AI CognoDB take-home assignment.

IMPORTANT:
I already have an existing project. DO NOT create a new project from scratch.
DO NOT delete or unnecessarily rewrite working code.
First inspect the entire existing project and understand what is already implemented.
Then complete the remaining work.

PROJECT:
Candidate–Job Skill Matching Application

TECH STACK:
- CognoDB Cloud
- Neo4j official Python driver
- openCypher
- Python
- FastAPI
- HTML/CSS/JavaScript frontend
- Environment variables using .env

CURRENT PROJECT STRUCTURE:

cognodb_job/
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── queries/
│   │   │   └── job_queries.py
│   │   ├── main.py
│   │   └── test_connection.py
│   │
│   ├── seed/
│   │   └── seed.py
│   │
│   └── venv/
│
├── frontend/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── requirement.md

MY EXISTING PROJECT STATUS:
- CognoDB/Neo4j connection has already been created.
- Graph data has already been created/seeded.
- Candidate, Job and Skill nodes/relationships exist.
- Candidate HAS_SKILL relationships exist.
- Job REQUIRES Skill relationships exist.
- A Cypher query for candidate-job skill matching has already been developed.
- The matching query calculates:
  - matching skills
  - matching skill count
  - required skill count
  - match percentage
- FastAPI has already been started.
- I am currently around the "Add Error Handling" stage.

EXISTING MATCHING LOGIC:
The existing logic is conceptually:

Candidate
  -[:HAS_SKILL]->
Skill
  <-[:REQUIRES]-
Job

For each job:
matchingSkills = skills shared by candidate and job
matchCount = number of matching skills
requiredSkillCount = number of required skills
matchPercentage = 100 * matchCount / requiredSkillCount

Preserve this logic unless inspection shows a genuine bug.

==================================================
PHASE 1 — INSPECT BEFORE CHANGING ANYTHING
==================================================

First inspect:

1. Every Python file in backend/app
2. database/connection.py
3. queries/job_queries.py
4. main.py
5. seed/seed.py
6. test_connection.py
7. requirements.txt
8. .env.example
9. .gitignore
10. frontend/
11. requirement.md

Understand:
- current database connection
- current Cypher queries
- current data model
- current FastAPI endpoints
- current frontend
- current dependencies
- what is already working

Do NOT immediately rewrite files.

After inspection, make a short internal implementation plan and then implement it.

==================================================
PHASE 2 — COMPLETE THE BACKEND
==================================================

Build a clean FastAPI backend around the existing implementation.

Use the official Neo4j Python driver.

Use environment variables for:

NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD

Never hard-code credentials.

Make sure database connections/sessions are handled safely.

Create a clean separation where practical:

database/
queries/
services/
API routes

Do not over-engineer the project.

==================================================
PHASE 3 — API ENDPOINTS
==================================================

Implement/fix useful endpoints such as:

GET /
    Health/application check

GET /candidates
    Return available candidates

GET /jobs
    Return available jobs

GET /skills
    Return available skills if useful

GET /match/{candidate_id}
    Return jobs ranked by match percentage for the candidate

The match response should contain useful information such as:

jobId
title
location
matchingSkills
matchCount
requiredSkillCount
matchPercentage

Use the existing matching Cypher logic.

Use PARAMETERIZED CYPHER QUERIES.

NEVER concatenate user input directly into Cypher.

For example, use parameters such as:

WHERE c.id = $candidate_id

rather than building Cypher strings using candidate IDs.

==================================================
PHASE 4 — ERROR HANDLING
==================================================

This is especially important.

Handle:

1. Candidate not found
   -> HTTP 404

2. Invalid/empty candidate ID
   -> HTTP 400

3. Database unavailable
   -> appropriate HTTP 500/503 response

4. Neo4j query/database errors
   -> graceful error response

5. Unexpected application errors
   -> graceful response

Do not expose passwords, connection strings, stack traces or sensitive information to the frontend.

The application must not crash when CognoDB is unavailable.

Return clear JSON error messages.

Example style:

{
  "detail": "Candidate C999 not found"
}

==================================================
PHASE 5 — DATA / CYPHER REQUIREMENTS
==================================================

Verify that the project satisfies the Wexa assignment requirements.

There must be:

- thoughtful graph model
- labeled nodes
- typed relationships
- useful properties
- realistic seed data
- seed script included in repository
- parameterized Cypher
- at least one multi-hop graph traversal
- at least one query demonstrating why a graph database is useful

Use the Candidate → Skill → Job relationship meaningfully.

Do not replace the existing data model unless it is fundamentally broken.

If something is missing, add it.

==================================================
PHASE 6 — FRONTEND
==================================================

Inspect the existing frontend first.

If it is incomplete, build a clean simple frontend.

The user should be able to:

1. Open the application
2. Enter/select a Candidate ID
3. Click a button such as "Find Matching Jobs"
4. Call the FastAPI backend
5. Display matching jobs

Display at minimum:

- Job title
- Job ID
- Location
- Matching skills
- Number of matching skills
- Required skills count
- Match percentage

Sort jobs by highest match percentage.

Make the interface clean and professional.

This is a take-home assignment, so do NOT make it look like an unfinished developer demo.

Include:

- clear navigation/header
- good spacing
- readable typography
- cards/table
- match percentage visualization if appropriate
- loading state
- empty state
- error state
- responsive layout

Do not introduce unnecessary frameworks if plain HTML/CSS/JavaScript is sufficient.

==================================================
PHASE 7 — CORS
==================================================

Configure FastAPI CORS properly so the frontend can communicate with the backend during development.

Do not use unsafe configuration unnecessarily.

Keep configuration easy to change.

==================================================
PHASE 8 — TESTING
==================================================

Test the complete application.

At minimum verify:

1. Backend starts successfully
2. Root endpoint works
3. Candidates endpoint works
4. Jobs endpoint works
5. Matching endpoint works
6. Valid candidate returns matching jobs
7. Invalid candidate returns 404
8. Empty/invalid candidate input is handled
9. Database failure is handled gracefully
10. Frontend successfully calls backend
11. Match percentage is calculated correctly
12. No credentials are exposed

If something fails, diagnose and fix it.

Do not simply tell me that a test failed.

==================================================
PHASE 9 — REQUIREMENTS
==================================================

Inspect requirements.txt.

Make sure all required dependencies are included, for example:

fastapi
uvicorn[standard]
neo4j
python-dotenv
pydantic
fastapi-cors / appropriate CORS support if actually required

Do not add unnecessary packages.

Make sure the project can be installed from requirements.txt.

==================================================
PHASE 10 — ENVIRONMENT SECURITY
==================================================

Verify:

.env exists for local use.

.env.example contains placeholders only.

Example:

NEO4J_URI=bolt+s://your-instance.databases.cognodb.cloud
NEO4J_USER=cognodb
NEO4J_PASSWORD=your_password_here

NEVER put the real password into .env.example.

Verify .env is ignored by .gitignore.

Never expose credentials in frontend code.

==================================================
PHASE 11 — README
==================================================

Create/update README.md so another developer can understand and run the project.

README must include:

1. Project title
2. Project overview
3. Problem being solved
4. Features
5. Technology stack
6. Why a graph database?
7. Graph data model
8. Node types
9. Relationship types
10. Explanation of the matching algorithm
11. Main Cypher queries
12. Project structure
13. CognoDB setup
14. Environment variables
15. Installation
16. Seed data instructions
17. Running FastAPI
18. Running frontend
19. API endpoints
20. Testing
21. Screenshots section
22. Deployment instructions if applicable

IMPORTANT:
Include a simple graph diagram in the README.

Example conceptual model:

Candidate
   |
   | HAS_SKILL
   v
 Skill
   ^
   | REQUIRES
   |
  Job

If the actual model contains additional nodes/relationships, document those too.

==================================================
PHASE 12 — PROJECT STRUCTURE
==================================================

Keep the project clean.

Aim for a structure similar to:

cognodb_job/
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── queries/
│   │   │   └── job_queries.py
│   │   ├── services/
│   │   │   └── matching_service.py
│   │   └── main.py
│   │
│   ├── seed/
│   │   └── seed.py
│   │
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Do not create duplicate files if equivalent files already exist.

==================================================
PHASE 13 — WEXA ASSIGNMENT CHECKLIST
==================================================

Before declaring the project complete, verify every requirement from the assignment:

DATA & QUERIES:
[ ] Thoughtful graph data model
[ ] Nodes/relationships/properties
[ ] Diagram in README
[ ] Realistic seed data
[ ] Seed script
[ ] Multi-hop traversal
[ ] Query that is naturally suited to graph DB
[ ] Parameterized Cypher
[ ] Official Neo4j driver

APPLICATION:
[ ] Functional web application
[ ] Non-technical user can use it
[ ] Clean UI
[ ] Loading state
[ ] Empty state
[ ] Error state
[ ] Readable typography
[ ] Good UX

ENGINEERING:
[ ] Environment variables
[ ] Credentials not committed
[ ] Clear project structure
[ ] Graceful database error handling
[ ] Maintainable code

DELIVERABLE:
[ ] Full source code
[ ] Seed scripts
[ ] Cypher queries
[ ] README
[ ] Graph model diagram
[ ] Setup instructions
[ ] Query explanations
[ ] Screenshot placeholders/section
[ ] Deployment-ready application

==================================================
VERY IMPORTANT DEVELOPMENT RULES
==================================================

1. DO NOT delete existing working code.

2. DO NOT replace my existing matching logic without a good technical reason.

3. DO NOT create fake database results just to make the UI work.

4. DO NOT hard-code candidate/job results.

5. DO NOT hard-code database credentials.

6. DO NOT use string concatenation for Cypher queries.

7. Use the existing CognoDB database.

8. Keep the code understandable because I must explain it during an interview.

9. Prefer simple solutions over unnecessary complexity.

10. If something is missing, implement it.

11. If something is broken, fix it.

12. If something is already correct, leave it alone.

13. After implementation, run tests and verify the application.

14. Do not stop after finding an error. Fix the error and continue.

15. Do not merely give me instructions for changes that you can safely make yourself. Make the changes in the project.

==================================================
FINAL OUTPUT
==================================================

When finished, provide me with:

1. What you changed
2. Files created
3. Files modified
4. API endpoints
5. How to start the backend
6. How to start the frontend
7. How to seed the database
8. What tests were run
9. Any remaining issues
10. A final Wexa assignment checklist showing PASS/NOT PASS for every requirement

MOST IMPORTANT:
Take ownership of completing the project end-to-end.
Inspect first.
Implement second.
Test third.
Fix problems.
Then give me the final status.

Do not stop at "Add Error Handling".
Complete the remaining project.