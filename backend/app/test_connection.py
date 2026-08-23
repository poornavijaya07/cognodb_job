import os
import sys

# Allow running this script from any directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import test_connection

try:
    result = test_connection()
    print("CognoDB connection successful!")
    print("Query result:", result)
except Exception as e:
    print(f"CognoDB connection failed: {e}")
    sys.exit(1)