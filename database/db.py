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
        # Check if pre-existing questions table needs question_text_hash column before script runs indexes
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if "questions" in tables:
            q_cols = [r["name"] for r in conn.execute("PRAGMA table_info(questions)").fetchall()]
            if "question_text_hash" not in q_cols:
                conn.execute("ALTER TABLE questions ADD COLUMN question_text_hash TEXT;")

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        # Check or set schema version
        row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
        if not row:
            conn.execute("INSERT INTO schema_version (version, applied_at) VALUES (?, ?)", 
                         (1, datetime.utcnow().isoformat()))

        # Ensure session_questions has shuffled_options and shuffled_correct columns
        sq_cols = [r["name"] for r in conn.execute("PRAGMA table_info(session_questions)").fetchall()]
        if "shuffled_options" not in sq_cols:
            conn.execute("ALTER TABLE session_questions ADD COLUMN shuffled_options TEXT;")
        if "shuffled_correct" not in sq_cols:
            conn.execute("ALTER TABLE session_questions ADD COLUMN shuffled_correct TEXT;")

        # Ensure questions has question_text_hash column and index
        q_cols = [r["name"] for r in conn.execute("PRAGMA table_info(questions)").fetchall()]
        if "question_text_hash" not in q_cols:
            conn.execute("ALTER TABLE questions ADD COLUMN question_text_hash TEXT;")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_q_text_hash ON questions(question_text_hash);")

        # Backfill any missing question_text_hash
        from services.duplicate_service import compute_question_hash, compute_question_text_hash
        missing_rows = conn.execute(
            "SELECT id, question_text, option_a, option_b, option_c, option_d FROM questions WHERE question_text_hash IS NULL OR question_text_hash = ''"
        ).fetchall()
        for mr in missing_rows:
            q_hash = compute_question_text_hash(mr["question_text"])
            opts = {"A": mr["option_a"], "B": mr["option_b"], "C": mr["option_c"], "D": mr["option_d"]}
            t_hash = compute_question_hash(mr["question_text"], opts)
            conn.execute(
                "UPDATE questions SET question_text_hash = ?, text_hash = ? WHERE id = ?",
                (q_hash, t_hash, mr["id"])
            )

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
