#!/usr/bin/env python3
"""
System Health Check Utility.

Inspects system environment, database connectivity, schema integrity,
repository layer, ML models, LLM connection, and directory structure.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import settings
from app.database import get_db_connection, verify_schema
from app.repositories.expense_repository import SQLiteExpenseRepository
from ml.model_manager import model_exists, validate_model


def run_health_check() -> bool:
    print("\n" + "=" * 50)
    print("        EXPENSE TRACKER HEALTH CHECK")
    print("=" * 50)

    all_ok = True
    results = []

    # 1. Python Environment
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    results.append(("Python Environment", f"v{py_ver}", True))

    # 2. Required Directories
    dirs_ok = (
        settings.data_dir.exists()
        and settings.logs_dir.exists()
        and settings.models_dir.exists()
    )
    results.append(("Required Directories", "OK" if dirs_ok else "Missing", dirs_ok))
    if not dirs_ok:
        all_ok = False

    # 3. Database File & Connection
    db_ok = False
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1;")
        db_ok = True
    except Exception as e:
        db_ok = False

    results.append(("Database Connection", "Connected" if db_ok else "Failed", db_ok))
    if not db_ok:
        all_ok = False

    # 4. Database Schema
    schema_ok = verify_schema()
    results.append(("Database Schema", "Verified" if schema_ok else "Invalid", schema_ok))
    if not schema_ok:
        all_ok = False

    # 5. Expense Repository
    repo_ok = False
    count_msg = "0 transactions"
    if db_ok and schema_ok:
        try:
            repo = SQLiteExpenseRepository()
            count = len(repo.get_all())
            repo_ok = True
            count_msg = f"{count:,} transactions"
        except Exception:
            repo_ok = False

    results.append(("Expense Repository", count_msg if repo_ok else "Error", repo_ok))
    if not repo_ok:
        all_ok = False

    # 6. ML Model Artifact
    ml_ok, ml_msg = validate_model()
    results.append(("ML Model Artifact", "Loaded" if ml_ok else ml_msg, ml_ok))
    # ML model missing is marked degraded but optional for basic operation

    # 7. LLM Provider Connection
    llm_ok = False
    llm_msg = "Unavailable"
    try:
        import ollama
        ollama.list()
        llm_ok = True
        llm_msg = f"Connected ({settings.llm_model})"
    except Exception:
        llm_ok = False
        llm_msg = f"Offline (start with: ollama serve)"

    results.append(("AI / LLM Provider", llm_msg, llm_ok))

    # Output Report
    print(f"\nComponent Status:")
    print("-" * 50)
    for comp, detail, status in results:
        mark = "OK" if status else "FAIL"
        print(f"  {comp:<22} [{mark:<4}]  {detail}")

    print("\n" + "=" * 50)
    if all_ok:
        print("System Status: HEALTHY")
    else:
        print("System Status: DEGRADED (Check issues above)")
    print("=" * 50)

    return all_ok


if __name__ == "__main__":
    run_health_check()
