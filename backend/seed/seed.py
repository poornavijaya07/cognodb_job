import os
import sys
from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase

# Allow importing database modules if needed and find .env
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(base_dir)
root_dir = os.path.dirname(backend_dir)

env_candidates = [
    os.path.join(backend_dir, ".env"),
    os.path.join(root_dir, ".env"),
    os.path.join(os.getcwd(), ".env"),
    find_dotenv()
]

for env_file in env_candidates:
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file, override=False)

URI = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI")
USERNAME = os.getenv("COGNODB_USERNAME") or os.getenv("NEO4J_USER") or os.getenv("COGNODB_USER")
PASSWORD = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD")

if not URI or not USERNAME or not PASSWORD:
    raise ValueError(
        "CognoDB/Neo4j credentials not found in environment. "
        "Please check your .env file."
    )

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def seed_database():
    """
    Clears existing graph data and seeds comprehensive, realistic Candidate, Job,
    Skill, and Company nodes and relationships.
    """
    with driver.session() as session:
        print("Clearing existing graph data...")
        session.run("MATCH (n) DETACH DELETE n")

        print("Creating Candidate nodes...")
        session.run("""
            CREATE
                (:Candidate {id: 'C001', name: 'John Smith', yearsExperience: 5, email: 'john.smith@example.com'}),
                (:Candidate {id: 'C002', name: 'Alice Johnson', yearsExperience: 3, email: 'alice.johnson@example.com'}),
                (:Candidate {id: 'C003', name: 'David Brown', yearsExperience: 7, email: 'david.brown@example.com'}),
                (:Candidate {id: 'C004', name: 'Emma Watson', yearsExperience: 4, email: 'emma.watson@example.com'}),
                (:Candidate {id: 'C005', name: 'Michael Chen', yearsExperience: 6, email: 'michael.chen@example.com'})
        """)

        print("Creating Skill nodes...")
        session.run("""
            CREATE
                (:Skill {id: 'S001', name: 'Python', category: 'Backend'}),
                (:Skill {id: 'S002', name: 'SQL', category: 'Database'}),
                (:Skill {id: 'S003', name: 'React', category: 'Frontend'}),
                (:Skill {id: 'S004', name: 'JavaScript', category: 'Frontend'}),
                (:Skill {id: 'S005', name: 'Node.js', category: 'Backend'}),
                (:Skill {id: 'S006', name: 'Java', category: 'Backend'}),
                (:Skill {id: 'S007', name: 'Docker', category: 'DevOps'}),
                (:Skill {id: 'S008', name: 'AWS', category: 'Cloud'}),
                (:Skill {id: 'S009', name: 'FastAPI', category: 'Backend'}),
                (:Skill {id: 'S010', name: 'TypeScript', category: 'Frontend'})
        """)

        print("Creating Job nodes...")
        session.run("""
            CREATE
                (:Job {id: 'J001', title: 'Python Backend Engineer', location: 'Bangalore', type: 'Full-time', minExperience: 3}),
                (:Job {id: 'J002', title: 'Full Stack Developer', location: 'Hyderabad', type: 'Full-time', minExperience: 2}),
                (:Job {id: 'J003', title: 'Frontend React Specialist', location: 'Remote', type: 'Full-time', minExperience: 2}),
                (:Job {id: 'J004', title: 'Senior Java Cloud Architect', location: 'Pune', type: 'Full-time', minExperience: 6}),
                (:Job {id: 'J005', title: 'Cloud Data Engineer', location: 'Bangalore', type: 'Full-time', minExperience: 4}),
                (:Job {id: 'J006', title: 'Node.js Microservices Developer', location: 'Gurgaon', type: 'Full-time', minExperience: 3})
        """)

        print("Creating Company nodes...")
        session.run("""
            CREATE
                (:Company {id: 'COMP001', name: 'CloudScale Technologies', industry: 'Enterprise Software'}),
                (:Company {id: 'COMP002', name: 'Nexus IT Solutions', industry: 'IT Consulting'}),
                (:Company {id: 'COMP003', name: 'Apex Digital Systems', industry: 'Fintech'}),
                (:Company {id: 'COMP004', name: 'Innovate AI Labs', industry: 'Artificial Intelligence'})
        """)

        print("Creating Candidate -> HAS_SKILL -> Skill relationships...")
        session.run("""
            MATCH
                (c1:Candidate {id: 'C001'}),
                (c2:Candidate {id: 'C002'}),
                (c3:Candidate {id: 'C003'}),
                (c4:Candidate {id: 'C004'}),
                (c5:Candidate {id: 'C005'}),
                (s1:Skill {id: 'S001'}),
                (s2:Skill {id: 'S002'}),
                (s3:Skill {id: 'S003'}),
                (s4:Skill {id: 'S004'}),
                (s5:Skill {id: 'S005'}),
                (s6:Skill {id: 'S006'}),
                (s7:Skill {id: 'S007'}),
                (s8:Skill {id: 'S008'}),
                (s9:Skill {id: 'S009'}),
                (s10:Skill {id: 'S010'})

            CREATE
                (c1)-[:HAS_SKILL {proficiency: 'Expert'}]->(s1),
                (c1)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s2),
                (c1)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s3),
                (c1)-[:HAS_SKILL {proficiency: 'Expert'}]->(s9),
                (c1)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s7),

                (c2)-[:HAS_SKILL {proficiency: 'Expert'}]->(s4),
                (c2)-[:HAS_SKILL {proficiency: 'Expert'}]->(s3),
                (c2)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s5),
                (c2)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s10),

                (c3)-[:HAS_SKILL {proficiency: 'Expert'}]->(s6),
                (c3)-[:HAS_SKILL {proficiency: 'Expert'}]->(s2),
                (c3)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s4),
                (c3)-[:HAS_SKILL {proficiency: 'Expert'}]->(s8),
                (c3)-[:HAS_SKILL {proficiency: 'Expert'}]->(s7),

                (c4)-[:HAS_SKILL {proficiency: 'Expert'}]->(s1),
                (c4)-[:HAS_SKILL {proficiency: 'Expert'}]->(s2),
                (c4)-[:HAS_SKILL {proficiency: 'Expert'}]->(s8),

                (c5)-[:HAS_SKILL {proficiency: 'Expert'}]->(s3),
                (c5)-[:HAS_SKILL {proficiency: 'Expert'}]->(s10),
                (c5)-[:HAS_SKILL {proficiency: 'Expert'}]->(s5),
                (c5)-[:HAS_SKILL {proficiency: 'Intermediate'}]->(s7)
        """)

        print("Creating Job -> REQUIRES -> Skill relationships...")
        session.run("""
            MATCH
                (j1:Job {id: 'J001'}),
                (j2:Job {id: 'J002'}),
                (j3:Job {id: 'J003'}),
                (j4:Job {id: 'J004'}),
                (j5:Job {id: 'J005'}),
                (j6:Job {id: 'J006'}),
                (s1:Skill {id: 'S001'}),
                (s2:Skill {id: 'S002'}),
                (s3:Skill {id: 'S003'}),
                (s4:Skill {id: 'S004'}),
                (s5:Skill {id: 'S005'}),
                (s6:Skill {id: 'S006'}),
                (s7:Skill {id: 'S007'}),
                (s8:Skill {id: 'S008'}),
                (s9:Skill {id: 'S009'}),
                (s10:Skill {id: 'S010'})

            CREATE
                (j1)-[:REQUIRES]->(s1),
                (j1)-[:REQUIRES]->(s2),
                (j1)-[:REQUIRES]->(s9),
                (j1)-[:REQUIRES]->(s7),

                (j2)-[:REQUIRES]->(s4),
                (j2)-[:REQUIRES]->(s3),
                (j2)-[:REQUIRES]->(s5),
                (j2)-[:REQUIRES]->(s2),

                (j3)-[:REQUIRES]->(s3),
                (j3)-[:REQUIRES]->(s4),
                (j3)-[:REQUIRES]->(s10),

                (j4)-[:REQUIRES]->(s6),
                (j4)-[:REQUIRES]->(s2),
                (j4)-[:REQUIRES]->(s8),
                (j4)-[:REQUIRES]->(s7),

                (j5)-[:REQUIRES]->(s1),
                (j5)-[:REQUIRES]->(s2),
                (j5)-[:REQUIRES]->(s8),

                (j6)-[:REQUIRES]->(s5),
                (j6)-[:REQUIRES]->(s4),
                (j6)-[:REQUIRES]->(s7)
        """)

        print("Creating Company -> OFFERS -> Job relationships...")
        session.run("""
            MATCH
                (co1:Company {id: 'COMP001'}),
                (co2:Company {id: 'COMP002'}),
                (co3:Company {id: 'COMP003'}),
                (co4:Company {id: 'COMP004'}),
                (j1:Job {id: 'J001'}),
                (j2:Job {id: 'J002'}),
                (j3:Job {id: 'J003'}),
                (j4:Job {id: 'J004'}),
                (j5:Job {id: 'J005'}),
                (j6:Job {id: 'J006'})

            CREATE
                (co1)-[:OFFERS]->(j1),
                (co2)-[:OFFERS]->(j2),
                (co3)-[:OFFERS]->(j3),
                (co1)-[:OFFERS]->(j4),
                (co4)-[:OFFERS]->(j5),
                (co2)-[:OFFERS]->(j6)
        """)

        print("Creating Candidate -> WORKED_AT -> Company relationships...")
        session.run("""
            MATCH
                (c1:Candidate {id: 'C001'}),
                (c2:Candidate {id: 'C002'}),
                (c3:Candidate {id: 'C003'}),
                (c4:Candidate {id: 'C004'}),
                (c5:Candidate {id: 'C005'}),
                (co1:Company {id: 'COMP001'}),
                (co2:Company {id: 'COMP002'}),
                (co3:Company {id: 'COMP003'}),
                (co4:Company {id: 'COMP004'})

            CREATE
                (c1)-[:WORKED_AT {role: 'Software Engineer', durationYears: 3}]->(co1),
                (c2)-[:WORKED_AT {role: 'Frontend Developer', durationYears: 2}]->(co2),
                (c3)-[:WORKED_AT {role: 'Senior Java Developer', durationYears: 4}]->(co3),
                (c4)-[:WORKED_AT {role: 'Data Analyst', durationYears: 2}]->(co4),
                (c5)-[:WORKED_AT {role: 'Full Stack Engineer', durationYears: 3}]->(co2)
        """)

        print("Database seeded successfully with rich sample graph data!")


if __name__ == "__main__":
    try:
        seed_database()
    finally:
        driver.close()