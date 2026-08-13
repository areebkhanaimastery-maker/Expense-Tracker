#!/usr/bin/env python3
"""
Database Backup Utility.

Creates timestamped copies of the active SQLite database in data/backups/
without overwriting existing backups.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import settings


def backup_database() -> Path | None:
    """
    Create a timestamped backup of the database file.
    """
    source = settings.database_path

    if not source.exists():
        print(f"Error: Database file does not exist at {source}")
        return None

    backups_dir = settings.data_dir / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"expenses_backup_{timestamp}.db"
    destination = backups_dir / backup_filename

    if destination.exists():
        print(f"Warning: Backup target {destination} already exists. Skipping.")
        return None

    try:
        shutil.copy2(source, destination)
        size_kb = destination.stat().st_size / 1024
        print("\n" + "=" * 50)
        print("         DATABASE BACKUP COMPLETED")
        print("=" * 50)
        print(f"Source      : {source}")
        print(f"Destination : {destination}")
        print(f"Backup Size : {size_kb:.2f} KB")
        print("=" * 50)
        return destination
    except Exception as e:
        print(f"Error creating database backup: {e}")
        return None


if __name__ == "__main__":
    backup_database()
