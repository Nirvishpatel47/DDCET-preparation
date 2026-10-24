import os
import sqlite3
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "ddcet.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

DEFAULT_SETTINGS = {
    "daily_target_minutes": "60",
    "session_default_size": "20",
    "priority_weight_weakness": "0.35",
    "priority_weight_revision": "0.25",
    "priority_weight_syllabus": "0.20",
    "priority_weight_neglect": "0.10",
    "priority_weight_speed": "0.10",
    "marking_correct": "1.0",
    "marking_incorrect": "-0.25",
    "marking_unanswered": "0.0",
    "mock_exam_duration_mins": "90",
    "mock_exam_total_questions": "100",
    "topic_max_cap_pct": "0.30"
}


def get_db_connection() -> sqlite3.Connection:
    """Provides a SQLite connection configured with WAL and foreign keys."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


@contextmanager
def get_db():
    """Context manager for transaction management."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initializes schema and seed default settings if not exists."""
    with get_db() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        # Check or set schema version
        row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
        if not row:
            conn.execute("INSERT INTO schema_version (version, applied_at) VALUES (?, ?)", 
                         (1, datetime.utcnow().isoformat()))

        # Populate default settings if missing
        for key, val in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)",
                (key, str(val), f"Default setting for {key}")
            )


def get_all_settings() -> Dict[str, Any]:
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        settings = {k: v for k, v in DEFAULT_SETTINGS.items()}
        for r in rows:
            settings[r["key"]] = r["value"]
        return settings


def update_setting(key: str, value: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))


def create_backup(label: Optional[str] = None) -> str:
    """Creates a timestamped backup of the SQLite database in the backups directory."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Primary database does not exist yet to backup.")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    backup_filename = f"ddcet_backup_{timestamp}{suffix}.db"
    backup_file_path = os.path.join(BACKUPS_DIR, backup_filename)

    # Use sqlite3 backup API for safe, live, transaction-consistent copy
    with sqlite3.connect(DB_PATH) as src_conn:
        with sqlite3.connect(backup_file_path) as dst_conn:
            src_conn.backup(dst_conn)
            
    return backup_file_path


def restore_backup(backup_path: str):
    """Restores database from a given backup file path."""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found at: {backup_path}")
    
    # Create safety backup of existing db first
    if os.path.exists(DB_PATH):
        safety_path = os.path.join(BACKUPS_DIR, f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy2(DB_PATH, safety_path)

    # Restore using sqlite3 backup API
    with sqlite3.connect(backup_path) as src_conn:
        with sqlite3.connect(DB_PATH) as dst_conn:
            src_conn.backup(dst_conn)


def list_backups() -> List[Dict[str, Any]]:
    """Lists all available backups with metadata."""
    if not os.path.exists(BACKUPS_DIR):
        return []
    
    backups = []
    for f in sorted(os.listdir(BACKUPS_DIR), reverse=True):
        if f.endswith(".db"):
            fp = os.path.join(BACKUPS_DIR, f)
            stat = os.stat(fp)
            backups.append({
                "filename": f,
                "filepath": fp,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    return backups
