# backend/app/tasks/backup.py
import os
import shutil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def run_backup():
    """
    Simulated backup task. 
    In production, this would use a tool like pg_dump or sqlite3 .backup
    """
    backup_dir = "backups"
    if not os.path.exists(backup_dir) and not os.environ.get("VERCEL"):
        os.makedirs(backup_dir)
        
    db_path = "rms_database.db" # Assuming SQLite for this project
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"rms_backup_{timestamp}.db")
        shutil.copy2(db_path, backup_file)
        logger.info(f"Database backup created: {backup_file}")
    else:
        logger.warning("Database file not found. Backup skipped.")

if __name__ == "__main__":
    run_backup()
