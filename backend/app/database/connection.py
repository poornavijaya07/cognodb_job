import os
from contextlib import contextmanager
from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError

# Load environment variables searching common locations
base_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/database
app_dir = os.path.dirname(base_dir)                    # backend/app
backend_dir = os.path.dirname(app_dir)                # backend
root_dir = os.path.dirname(backend_dir)                # root

env_candidates = [
    os.path.join(backend_dir, ".env"),
    os.path.join(root_dir, ".env"),
    os.path.join(os.getcwd(), ".env"),
    os.path.join(os.getcwd(), "backend", ".env"),
    find_dotenv()
]

for env_file in env_candidates:
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file, override=False)

COGNODB_URI = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI")
COGNODB_USERNAME = os.getenv("COGNODB_USERNAME") or os.getenv("NEO4J_USER") or os.getenv("COGNODB_USER")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD")

_driver: Driver | None = None


def get_driver() -> Driver:
    """
    Returns the Neo4j/CognoDB driver instance, creating it if not already initialized.
    """
    global _driver
    if _driver is None:
        if not COGNODB_URI or not COGNODB_USERNAME or not COGNODB_PASSWORD:
            raise ValueError(
                "CognoDB/Neo4j credentials are not configured. "
                "Please check your .env file for COGNODB_URI, COGNODB_USERNAME, and COGNODB_PASSWORD."
            )
        _driver = GraphDatabase.driver(
            COGNODB_URI,
            auth=(COGNODB_USERNAME, COGNODB_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60.0
        )
    return _driver


# Direct driver alias for backward compatibility with existing code
try:
    driver = get_driver()
except Exception:
    driver = None


@contextmanager
def get_db_session():
    """
    Context manager providing a safe Neo4j session.
    Automatically handles session closing and error propagation.
    """
    drv = get_driver()
    session = drv.session()
    try:
        yield session
    finally:
        session.close()


def test_connection():
    """
    Verifies connection to CognoDB/Neo4j database.
    """
    with get_db_session() as session:
        result = session.run("RETURN 1 AS result")
        record = result.single()
        return record["result"] if record else 1


def close_driver():
    """
    Closes the global database driver connection gracefully.
    """
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
