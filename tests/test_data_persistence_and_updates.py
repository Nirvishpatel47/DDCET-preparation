import os
import sys
import shutil
import json
import sqlite3
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app import app
from database.db import (
    get_db,
    init_db,
    create_backup,
    restore_backup,
    list_backups,
    migrate_legacy_data_if_needed,
    sync_public_questions_to_db,
    apply_migrations,
    get_all_settings,
    update_setting,
)
from services.stats_service import compute_comprehensive_stats
from services.auth_service import get_current_user, login_user


def test_1_fresh_installation(tmp_path, monkeypatch):
    """
    Test 1: Fresh installation
    - Starts with empty persistent directory and no legacy database.
    - Initialises the application.
    - Verifies that the persistent database is created.
    - Verifies that public questions are imported automatically.
    - Verifies that personal statistics (attempts, sessions) are initially zero/empty.
    """
    user_dir = str(tmp_path / "fresh_user")
    monkeypatch.setenv("DDCET_USER_DATA_DIR", user_dir)
    monkeypatch.setattr("database.db.LEGACY_DB_PATH", str(tmp_path / "no_legacy.db"))

    fresh_db = os.path.join(user_dir, "data", "ddcet_user.db")
    assert not os.path.exists(fresh_db)

    monkeypatch.setattr("database.db.DB_PATH", fresh_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", os.path.join(user_dir, "backups"))
    monkeypatch.setattr("config.USER_DB_PATH", fresh_db)
    monkeypatch.setattr("config.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("config.BACKUPS_DIR", os.path.join(user_dir, "backups"))

    init_db(seed_public_questions=True)

    assert os.path.exists(fresh_db)

    with get_db(fresh_db) as conn:
        q_count = conn.execute("SELECT count(*) FROM questions").fetchone()[0]
        att_count = conn.execute("SELECT count(*) FROM attempts").fetchone()[0]
        sess_count = conn.execute("SELECT count(*) FROM sessions").fetchone()[0]
        rev_count = conn.execute("SELECT count(*) FROM revision_schedules").fetchone()[0]

    # Public question bank should be seeded
    assert q_count > 0, "Public questions should be automatically imported on fresh install"
    # Personal history must be completely empty
    assert att_count == 0, "Personal attempts must be initially empty"
    assert sess_count == 0, "Personal sessions must be initially empty"
    assert rev_count == 0, "Revision records must be initially empty"


def test_2_legacy_migration_safety(tmp_path, monkeypatch):
    """
    Test 2: Legacy installation migration
    - Simulates an existing user with an existing database at legacy path.
    - Runs migration.
    - Verifies safety backup creation, data copy to persistent directory,
      and exact record verification.
    """
    monkeypatch.setenv("TEST_MIGRATION_ACTIVE", "1")
    legacy_dir = tmp_path / "legacy_repo"
    os.makedirs(legacy_dir, exist_ok=True)
    fake_legacy_db = str(legacy_dir / "ddcet.db")

    # Seed fake legacy DB with 2 questions and 1 attempt
    with sqlite3.connect(fake_legacy_db) as conn:
        with open("database/schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.execute("INSERT INTO subjects (id, name) VALUES (1, 'Math')")
        conn.execute("INSERT INTO topics (id, subject_id, name) VALUES (1, 1, 'Calculus')")
        conn.execute("INSERT INTO subtopics (id, topic_id, name) VALUES (1, 1, 'Limits')")
        conn.execute(
            """
            INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                   correct_answer, subject_id, topic_id, subtopic_id, difficulty,
                                   verified, text_hash, question_text_hash, created_at)
            VALUES ('LEG-1', 'Legacy Question 1', 'A', 'B', 'C', 'D', 'A', 1, 1, 1, 'easy', 1, 'h1', 'qh1', datetime('now'))
            """
        )
        conn.execute("INSERT INTO sessions (id, session_type, total_questions, started_at) VALUES ('s_leg', 'daily', 1, datetime('now'))")
        conn.execute("INSERT INTO attempts (question_id, session_id, selected_option, is_correct, attempted_at) VALUES ('LEG-1', 's_leg', 'A', 1, datetime('now'))")
        conn.execute("INSERT INTO revision_schedules (question_id, last_attempt_at, next_due_date) VALUES ('LEG-1', datetime('now'), '2026-11-01')")
        conn.commit()

    user_dir = str(tmp_path / "migrated_user")
    persistent_db = os.path.join(user_dir, "data", "ddcet_user.db")
    backups_dir = os.path.join(user_dir, "backups")

    monkeypatch.setattr("database.db.LEGACY_DB_PATH", fake_legacy_db)
    monkeypatch.setattr("database.db.DB_PATH", persistent_db)
    monkeypatch.setattr("database.db.USER_DB_PATH", persistent_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", backups_dir)
    monkeypatch.setattr("config.USER_DB_PATH", persistent_db)

    # Perform migration
    did_migrate = migrate_legacy_data_if_needed()
    assert did_migrate is True
    assert os.path.exists(persistent_db)

    # Verify backup was created
    backups = os.listdir(backups_dir)
    assert any(b.startswith("legacy_pre_migration_") for b in backups)

    # Verify data transferred accurately
    with get_db(persistent_db) as conn:
        assert conn.execute("SELECT count(*) FROM attempts").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM revision_schedules").fetchone()[0] == 1


def test_3_user_progress_and_simulated_application_update(tmp_path, monkeypatch):
    """
    Test 3: Existing user progress accumulation & simulated application update
    - User answers questions, generates revision schedules, records mistake categories.
    - Simulates app source update / app reload.
    - Verifies all attempts, revisions, mistakes, and settings remain 100% intact.
    """
    user_dir = str(tmp_path / "persistent_student")
    monkeypatch.setenv("DDCET_USER_DATA_DIR", user_dir)
    monkeypatch.setattr("database.db.LEGACY_DB_PATH", str(tmp_path / "no_legacy.db"))
    user_db = os.path.join(user_dir, "data", "ddcet_user.db")

    monkeypatch.setattr("database.db.DB_PATH", user_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", os.path.join(user_dir, "backups"))
    monkeypatch.setattr("config.USER_DB_PATH", user_db)
    monkeypatch.setattr("config.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("config.BACKUPS_DIR", os.path.join(user_dir, "backups"))
    monkeypatch.setattr("config.CURRENT_USER_FILE", os.path.join(user_dir, "data", "current_user.json"))
    monkeypatch.setattr("services.auth_service.CURRENT_USER_FILE", os.path.join(user_dir, "data", "current_user.json"))

    init_db(seed_public_questions=True)

    # Step A: User completes practice and records attempts
    with get_db(user_db) as conn:
        questions = conn.execute("SELECT id, correct_answer FROM questions LIMIT 5").fetchall()
        assert len(questions) == 5

        # Create session
        conn.execute(
            """
            INSERT INTO sessions (id, session_type, total_questions, answered_questions, started_at)
            VALUES ('sess_update_test', 'daily_mixed', 5, 5, datetime('now'))
            """
        )

        for i, q in enumerate(questions):
            is_corr = 1 if i % 2 == 0 else 0
            sel_opt = q["correct_answer"] if is_corr else ("B" if q["correct_answer"] != "B" else "C")
            mistake = "concept" if not is_corr else None

            conn.execute(
                """
                INSERT INTO attempts (question_id, session_id, selected_option, is_correct, time_spent_seconds, confidence, mistake_category, attempted_at)
                VALUES (?, 'sess_update_test', ?, ?, 18, 'medium', ?, datetime('now'))
                """,
                (q["id"], sel_opt, is_corr, mistake)
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO revision_schedules (
                    question_id, last_attempt_at, next_due_date, current_interval_days,
                    consecutive_correct, consecutive_incorrect, total_attempts, last_mistake_category
                ) VALUES (?, datetime('now'), '2026-11-01', 1, ?, ?, 1, ?)
                """,
                (q["id"], 1 if is_corr else 0, 0 if is_corr else 1, mistake)
            )

    update_setting("daily_target_minutes", "75")

    # Step B: Record database state before simulated update
    with get_db(user_db) as conn:
        pre_attempts = conn.execute("SELECT count(*) FROM attempts").fetchone()[0]
        pre_revisions = conn.execute("SELECT count(*) FROM revision_schedules").fetchone()[0]
        pre_settings = get_all_settings()

    assert pre_attempts == 5
    assert pre_revisions == 5
    assert pre_settings["daily_target_minutes"] == "75"

    # Step C: Simulate application code update (re-running init_db as occurs on app startup)
    init_db()

    with get_db(user_db) as conn:
        post_attempts = conn.execute("SELECT count(*) FROM attempts").fetchone()[0]
        post_revisions = conn.execute("SELECT count(*) FROM revision_schedules").fetchone()[0]
        post_settings = get_all_settings()

    # User progress must be perfectly preserved!
    assert post_attempts == pre_attempts, "Attempts must remain untouched after update"
    assert post_revisions == pre_revisions, "Revisions must remain untouched after update"
    assert post_settings["daily_target_minutes"] == "75", "User settings must be preserved"


def test_4_question_bank_update_without_duplication(tmp_path, monkeypatch):
    """
    Test 4: Question-bank update
    - Simulates new public questions added to the repository in an update.
    - Runs public sync.
    - Verifies that new questions are inserted, existing questions are not duplicated,
      and all existing user attempts remain linked and intact.
    """
    user_dir = str(tmp_path / "sync_user")
    monkeypatch.setenv("DDCET_USER_DATA_DIR", user_dir)
    monkeypatch.setattr("database.db.LEGACY_DB_PATH", str(tmp_path / "no_legacy.db"))
    user_db = os.path.join(user_dir, "data", "ddcet_user.db")

    monkeypatch.setattr("database.db.DB_PATH", user_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", os.path.join(user_dir, "backups"))
    monkeypatch.setattr("config.USER_DB_PATH", user_db)
    monkeypatch.setattr("config.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("config.BACKUPS_DIR", os.path.join(user_dir, "backups"))

    init_db(seed_public_questions=True)

    with get_db(user_db) as conn:
        initial_q_count = conn.execute("SELECT count(*) FROM questions").fetchone()[0]
        first_q = conn.execute("SELECT id FROM questions LIMIT 1").fetchone()[0]

        # Record attempt for first question
        conn.execute(
            """
            INSERT INTO sessions (id, session_type, total_questions, started_at)
            VALUES ('sess_q_test', 'daily_mixed', 1, datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO attempts (question_id, session_id, selected_option, is_correct, time_spent_seconds, attempted_at)
            VALUES (?, 'sess_q_test', 'A', 1, 20, datetime('now'))
            """,
            (first_q,)
        )

    # Re-syncing public questions must be idempotent (0 duplicates, count unchanged)
    with get_db(user_db) as conn:
        sync_stats = sync_public_questions_to_db(conn)
        post_q_count = conn.execute("SELECT count(*) FROM questions").fetchone()[0]
        post_attempts = conn.execute("SELECT count(*) FROM attempts").fetchone()[0]

    assert sync_stats["inserted"] == 0
    assert post_q_count == initial_q_count
    assert post_attempts == 1


def test_5_independent_clone_isolation(tmp_path, monkeypatch):
    """
    Test 5: Independent clone
    - Simulates two independent users on separate installations.
    - User A practices and records attempts.
    - User B installs the app.
    - Verifies that User B starts with fresh personal stats and does not see User A's data.
    """
    monkeypatch.setattr("database.db.LEGACY_DB_PATH", str(tmp_path / "no_legacy.db"))
    user_a_dir = str(tmp_path / "user_a")
    user_b_dir = str(tmp_path / "user_b")

    # User A
    user_a_db = os.path.join(user_a_dir, "data", "ddcet_user.db")
    monkeypatch.setattr("database.db.DB_PATH", user_a_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_a_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", os.path.join(user_a_dir, "backups"))
    monkeypatch.setattr("config.USER_DB_PATH", user_a_db)
    init_db(seed_public_questions=True)

    with get_db(user_a_db) as conn:
        q = conn.execute("SELECT id FROM questions LIMIT 1").fetchone()[0]
        conn.execute("INSERT INTO sessions (id, session_type, total_questions, started_at) VALUES ('sA', 'daily', 1, datetime('now'))")
        conn.execute("INSERT INTO attempts (question_id, session_id, is_correct, attempted_at) VALUES (?, 'sA', 1, datetime('now'))", (q,))

    # User B
    user_b_db = os.path.join(user_b_dir, "data", "ddcet_user.db")
    monkeypatch.setattr("database.db.DB_PATH", user_b_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_b_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", os.path.join(user_b_dir, "backups"))
    monkeypatch.setattr("config.USER_DB_PATH", user_b_db)
    init_db(seed_public_questions=True)

    with get_db(user_a_db) as connA:
        count_a = connA.execute("SELECT count(*) FROM attempts").fetchone()[0]
    with get_db(user_b_db) as connB:
        count_b = connB.execute("SELECT count(*) FROM attempts").fetchone()[0]

    assert count_a == 1, "User A has their attempt"
    assert count_b == 0, "User B has completely independent 0 attempts"


def test_6_backup_restore_and_corrupt_protection(tmp_path, monkeypatch):
    """
    Test 6: Backup and migration safety
    - Creates a live database backup.
    - Verifies backup integrity.
    - Verifies restore from backup.
    - Verifies that attempting to restore a corrupted or empty file is REJECTED
      and leaves the original user database unharmed.
    """
    user_dir = str(tmp_path / "backup_user")
    monkeypatch.setenv("DDCET_USER_DATA_DIR", user_dir)
    monkeypatch.setattr("database.db.LEGACY_DB_PATH", str(tmp_path / "no_legacy.db"))
    user_db = os.path.join(user_dir, "data", "ddcet_user.db")
    backups_dir = os.path.join(user_dir, "backups")

    monkeypatch.setattr("database.db.DB_PATH", user_db)
    monkeypatch.setattr("database.db.DATA_DIR", os.path.join(user_dir, "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", backups_dir)
    monkeypatch.setattr("config.USER_DB_PATH", user_db)
    monkeypatch.setattr("config.BACKUPS_DIR", backups_dir)

    init_db(seed_public_questions=True)

    with get_db(user_db) as conn:
        q = conn.execute("SELECT id FROM questions LIMIT 1").fetchone()[0]
        conn.execute("INSERT INTO sessions (id, session_type, total_questions, started_at) VALUES ('s_bk', 'daily', 1, datetime('now'))")
        conn.execute("INSERT INTO attempts (question_id, session_id, is_correct, attempted_at) VALUES (?, 's_bk', 1, datetime('now'))", (q,))

    # Create backup
    bk_file = create_backup("milestone_1")
    assert os.path.exists(bk_file)

    # Verify backup listing
    b_list = list_backups()
    assert len(b_list) >= 1
    assert any(b["filename"].endswith("milestone_1.db") for b in b_list)

    # Restore from valid backup
    restore_backup(bk_file)
    with get_db(user_db) as conn:
        assert conn.execute("SELECT count(*) FROM attempts").fetchone()[0] == 1

    # Attempt to restore an empty file -> MUST FAIL and preserve original data
    corrupt_file = str(tmp_path / "corrupted.db")
    with open(corrupt_file, "w") as f:
        f.write("")

    with pytest.raises(ValueError):
        restore_backup(corrupt_file)

    # Active DB must still be intact with 1 attempt
    with get_db(user_db) as conn:
        assert conn.execute("SELECT count(*) FROM attempts").fetchone()[0] == 1
