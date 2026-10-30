import os
import sqlite3
import shutil
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

from config import (
    BASE_DIR,
    REPO_DATA_DIR,
    LEGACY_DB_PATH,
    LEGACY_CURRENT_USER_FILE,
    LEGACY_FRIENDS_CACHE_FILE,
    LEGACY_SYNC_QUEUE_FILE,
    LEGACY_FRIENDS_FILE,
    USER_DB_PATH,
    PERSISTENT_DATA_DIR,
    PERSISTENT_BACKUPS_DIR,
    CURRENT_USER_FILE,
    FRIENDS_FILE,
    FRIENDS_CACHE_FILE,
    SYNC_QUEUE_FILE,
)

SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# Active database and backups paths point to persistent user data location
DB_PATH = USER_DB_PATH
DATA_DIR = PERSISTENT_DATA_DIR
BACKUPS_DIR = PERSISTENT_BACKUPS_DIR

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


def get_db_connection(db_file: Optional[str] = None) -> sqlite3.Connection:
    """Provides a SQLite connection configured with WAL and foreign keys."""
    target_path = db_file or DB_PATH
    conn = sqlite3.connect(target_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


@contextmanager
def get_db(db_file: Optional[str] = None):
    """Context manager for transaction management."""
    conn = get_db_connection(db_file)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_legacy_data_if_needed() -> bool:
    """
    Migrates user personal data and SQLite database from the legacy repository location
    (<repo>/data/ddcet.db) to the external persistent directory (~/.ddcet-preparation/data/ddcet_user.db).
    Creates safe pre-migration backups in both locations, copies the database using SQLite backup API,
    migrates personal JSON files, and verifies table counts before completing.
    The legacy database in the repo is preserved intact.
    """
    if os.path.exists(DB_PATH):
        # Persistent user database already exists
        return False

    # If running inside pytest, only migrate if explicitly enabled for a migration test
    if os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("TEST_MIGRATION_ACTIVE"):
        return False

    # Only migrate if DB_PATH is the active USER_DB_PATH
    if os.path.abspath(DB_PATH) != os.path.abspath(USER_DB_PATH):
        return False

    if not LEGACY_DB_PATH or not os.path.exists(LEGACY_DB_PATH):
        # Fresh installation with no legacy DB
        return False

    print(f"[database] Detected existing user database at: {LEGACY_DB_PATH}")
    print(f"[database] Initiating safe migration to persistent storage: {DB_PATH}")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    # 1. Create safety backup of legacy database in both persistent backups and repo backups
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"legacy_pre_migration_{ts}.db"
    persistent_backup_file = os.path.join(BACKUPS_DIR, backup_name)
    repo_backups_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(repo_backups_dir, exist_ok=True)
    repo_backup_file = os.path.join(repo_backups_dir, backup_name)

    with sqlite3.connect(LEGACY_DB_PATH) as src_conn:
        with sqlite3.connect(persistent_backup_file) as dst_conn:
            src_conn.backup(dst_conn)
        with sqlite3.connect(repo_backup_file) as dst_conn2:
            src_conn.backup(dst_conn2)

    # 2. Copy database to persistent location using live backup API
    with sqlite3.connect(LEGACY_DB_PATH) as src_conn:
        with sqlite3.connect(DB_PATH) as dst_conn:
            src_conn.backup(dst_conn)

    # 3. Migrate personal JSON files if they exist in repo and not in persistent directory
    json_migrations = [
        (LEGACY_CURRENT_USER_FILE, CURRENT_USER_FILE),
        (LEGACY_FRIENDS_FILE, FRIENDS_FILE),
        (LEGACY_FRIENDS_CACHE_FILE, FRIENDS_CACHE_FILE),
        (LEGACY_SYNC_QUEUE_FILE, SYNC_QUEUE_FILE),
    ]
    for src_f, dst_f in json_migrations:
        if os.path.exists(src_f) and not os.path.exists(dst_f):
            try:
                shutil.copy2(src_f, dst_f)
                print(f"[database] Migrated {os.path.basename(src_f)} to persistent user data directory.")
            except Exception as e:
                print(f"[database] Notice copying {src_f}: {e}")

    # 4. Verify record integrity between legacy and migrated database
    with sqlite3.connect(LEGACY_DB_PATH) as src_conn:
        src_conn.row_factory = sqlite3.Row
        with sqlite3.connect(DB_PATH) as dst_conn:
            dst_conn.row_factory = sqlite3.Row
            for tbl in ["questions", "sessions", "attempts", "revision_schedules"]:
                s_cnt = src_conn.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
                d_cnt = dst_conn.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
                if s_cnt != d_cnt:
                    raise RuntimeError(
                        f"Migration verification failed for table '{tbl}': source has {s_cnt} records, migrated has {d_cnt}"
                    )

    print(f"[database] Migration verified successfully. User progress transferred to {DB_PATH}.")
    print(f"[database] Original database preserved at {LEGACY_DB_PATH}.")
    return True


def sync_public_questions_to_db(conn: sqlite3.Connection) -> Dict[str, int]:
    """
    Safely and idempotently syncs questions from the public repository question bank
    into the user's persistent SQLite database.
    - Never overwrites or resets user attempts, sessions, or revision schedules.
    - Never deletes any questions that have associated user attempts or revision records.
    - Inserts new questions without duplicating existing ones.
    - Preserves existing question IDs.
    """
    from services.validation_service import get_or_create_hierarchy
    from services.duplicate_service import compute_question_hash, compute_question_text_hash, check_duplicate_fast

    public_files = [
        os.path.join(REPO_DATA_DIR, "ddcet_2027_question_bank.json"),
        os.path.join(REPO_DATA_DIR, "data.json"),
        os.path.join(REPO_DATA_DIR, "ddcet_canonical_questions.json"),
    ]

    existing_rows = conn.execute("SELECT id, text_hash, question_text_hash FROM questions").fetchall()
    existing_ids = {r[0] for r in existing_rows}
    existing_text_hashes = {r[1] for r in existing_rows if r[1]}
    existing_q_hashes = {r[2] for r in existing_rows if r[2]}

    stats = {"inserted": 0, "skipped_existing": 0, "skipped_duplicates": 0}

    for pub_file in public_files:
        if not os.path.exists(pub_file):
            continue

        try:
            with open(pub_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    continue
        except Exception as e:
            print(f"[database] Error reading public question bank {pub_file}: {e}")
            continue

        for q in data:
            if not isinstance(q, dict) or "id" not in q or "question" not in q:
                continue

            qid = q["id"]
            if qid in existing_ids:
                stats["skipped_existing"] += 1
                continue

            opts = q.get("options", {})
            if not isinstance(opts, dict) or not all(k in opts for k in ["A", "B", "C", "D"]):
                continue

            # Compute hashes
            t_hash = compute_question_hash(q["question"], opts)
            q_hash = compute_question_text_hash(q["question"])

            # Fast duplicate check
            if t_hash in existing_text_hashes or q_hash in existing_q_hashes:
                stats["skipped_duplicates"] += 1
                continue

            dup = check_duplicate_fast(conn, qid, q["question"], opts)
            if dup:
                stats["skipped_duplicates"] += 1
                continue

            # Resolve hierarchy
            sub_name = q.get("subject", "General Aptitude")
            top_name = q.get("topic", "General")
            subtop_name = q.get("subtopic", "Core Concepts")

            sub_id, top_id, subtop_id = get_or_create_hierarchy(conn, sub_name, top_name, subtop_name)

            source_json = json.dumps(q.get("source", {}))
            tags_json = json.dumps(q.get("tags", []))
            verified_int = 1 if q.get("verified") else 0
            created_at = q.get("created_at") or datetime.utcnow().isoformat()
            correct_ans = q.get("correct_answer", "A").upper()
            if correct_ans not in ("A", "B", "C", "D"):
                correct_ans = "A"

            conn.execute(
                """
                INSERT INTO questions (
                    id, question_text, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, subject_id, topic_id, subtopic_id,
                    difficulty, source_json, tags_json, verified, text_hash, question_text_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    qid, q["question"], opts["A"], opts["B"], opts["C"], opts["D"],
                    correct_ans, q.get("explanation", ""), sub_id, top_id, subtop_id,
                    q.get("difficulty", "medium"), source_json, tags_json, verified_int,
                    t_hash, q_hash, created_at
                )
            )

            existing_ids.add(qid)
            existing_text_hashes.add(t_hash)
            existing_q_hashes.add(q_hash)
            stats["inserted"] += 1

    return stats


def apply_migrations(conn: sqlite3.Connection):
    """
    Version-controlled, incremental schema migrations.
    - Tracks applied version in schema_version table.
    - Applies migrations sequentially in transactions.
    - Preserves all existing records.
    """
    # Ensure schema_version table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );
    """)

    row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
    current_version = row[0] if row else 0

    # Migration 1: Baseline schema (tables from schema.sql)
    if current_version < 1:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.execute("INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (1, ?)",
                     (datetime.utcnow().isoformat(),))
        current_version = 1

    # Migration 2: Ensure question_text_hash column & index, shuffled options in session_questions
    if current_version < 2:
        q_cols = [r["name"] for r in conn.execute("PRAGMA table_info(questions)").fetchall()]
        if "question_text_hash" not in q_cols:
            conn.execute("ALTER TABLE questions ADD COLUMN question_text_hash TEXT;")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_q_text_hash ON questions(question_text_hash);")

        sq_cols = [r["name"] for r in conn.execute("PRAGMA table_info(session_questions)").fetchall()]
        if "shuffled_options" not in sq_cols:
            conn.execute("ALTER TABLE session_questions ADD COLUMN shuffled_options TEXT;")
        if "shuffled_correct" not in sq_cols:
            conn.execute("ALTER TABLE session_questions ADD COLUMN shuffled_correct TEXT;")

        conn.execute("INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (2, ?)",
                     (datetime.utcnow().isoformat(),))
        current_version = 2

    # Migration 3: Performance indexes and safety guarantees
    if current_version < 3:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id, attempted_at);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_revision_due ON revision_schedules(next_due_date);")
        conn.execute("INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (3, ?)",
                     (datetime.utcnow().isoformat(),))
        current_version = 3


def init_db(seed_public_questions: Optional[bool] = None):
    """
    Initializes database with full user progress protection:
    1. Detects and migrates existing user data if found in legacy repository location.
    2. Runs schema initialization or incremental migrations.
    3. Populates missing default settings.
    4. Safely syncs public questions without duplicating or resetting user progress.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    # Check for legacy migration first
    migrate_legacy_data_if_needed()

    with get_db() as conn:
        # Apply version-controlled schema migrations
        apply_migrations(conn)

        # Populate default settings if missing
        for key, val in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)",
                (key, str(val), f"Default setting for {key}")
            )

        # Idempotently sync public question bank:
        # By default seeds during normal app runs, or when explicitly requested in test fixtures
        should_seed = seed_public_questions if seed_public_questions is not None else (not os.environ.get("PYTEST_CURRENT_TEST"))
        if should_seed:
            sync_public_questions_to_db(conn)


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
    """Creates a timestamped backup of the persistent SQLite database in the backups directory."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Primary database does not exist yet to backup.")
    
    os.makedirs(BACKUPS_DIR, exist_ok=True)
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
    """
    Restores database from a given backup file path with pre-validation and safety backup.
    Guarantees that a corrupted or empty file cannot destroy the user's active database.
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found at: {backup_path}")

    # 1. Validate that backup_path is a non-empty, valid SQLite database with required tables
    if os.path.getsize(backup_path) == 0:
        raise ValueError("Backup file is empty (0 bytes). Restoration aborted.")

    try:
        with sqlite3.connect(backup_path) as test_conn:
            test_conn.execute("PRAGMA quick_check")
            tables = [r[0] for r in test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "questions" not in tables or "schema_version" not in tables:
                raise ValueError("Backup file is missing required tables (questions, schema_version). Restoration aborted.")
    except Exception as e:
        raise ValueError(f"Backup file validation failed: {e}")

    # 2. Create safety backup of existing db first
    if os.path.exists(DB_PATH):
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        safety_path = os.path.join(BACKUPS_DIR, f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        with sqlite3.connect(DB_PATH) as src_conn:
            with sqlite3.connect(safety_path) as dst_conn:
                src_conn.backup(dst_conn)

    # 3. Restore using sqlite3 backup API
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
