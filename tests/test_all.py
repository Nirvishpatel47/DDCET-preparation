import os
import json
import pytest
import sqlite3
from datetime import datetime, date, timedelta

# Ensure project root is in sys.path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db, init_db, DB_PATH, create_backup, restore_backup, list_backups, get_all_settings, update_setting
from models.schemas import QuestionModel
from services.validation_service import validate_and_prepare_question, get_or_create_hierarchy
from services.duplicate_service import compute_question_hash, check_exact_duplicate, find_probable_duplicates, calculate_similarity
from services.import_export_service import process_import, export_questions, export_quarantined_records
from services.practice_service import create_practice_session, record_question_answer, complete_session, get_session_state
from services.revision_service import update_spaced_repetition, get_due_revisions, get_mistake_patterns
from services.adaptive_service import calculate_adaptive_priorities
from services.analytics_service import get_dashboard_analytics


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use an isolated SQLite test database for each test session."""
    test_db_file = str(tmp_path / "test_ddcet.db")
    monkeypatch.setattr("database.db.DB_PATH", test_db_file)
    monkeypatch.setattr("database.db.DATA_DIR", str(tmp_path))
    monkeypatch.setattr("database.db.BACKUPS_DIR", str(tmp_path / "backups"))
    os.makedirs(str(tmp_path / "backups"), exist_ok=True)
    init_db()
    yield test_db_file


# =====================================================================
# 1. QUESTION VALIDATION TESTS
# =====================================================================

def test_valid_question_schema():
    valid_data = {
        "id": "MATH-001",
        "question": "What is the derivative of x^2?",
        "options": {"A": "2x", "B": "x", "C": "x^3", "D": "2"},
        "correct_answer": "A",
        "explanation": "Using power rule: d/dx(x^n) = n*x^(n-1).",
        "subject": "Mathematics",
        "topic": "Calculus",
        "subtopic": "Derivatives",
        "difficulty": "easy",
        "verified": True
    }
    model = QuestionModel(**valid_data)
    assert model.id == "MATH-001"
    assert model.correct_answer == "A"
    assert model.verified is True


def test_reject_less_than_four_options():
    invalid_data = {
        "id": "MATH-002",
        "question": "What is 2 + 2?",
        "options": {"A": "4", "B": "5", "C": "6"}, # Missing D
        "correct_answer": "A",
        "subject": "Mathematics",
        "topic": "Arithmetic",
        "subtopic": "Addition",
        "difficulty": "easy"
    }
    with pytest.raises(Exception) as exc:
        QuestionModel(**invalid_data)
    assert "Options must contain exactly keys A, B, C, and D" in str(exc.value)


def test_reject_invalid_correct_answer_key():
    invalid_data = {
        "id": "MATH-003",
        "question": "What is 2 + 2?",
        "options": {"A": "4", "B": "5", "C": "6", "D": "7"},
        "correct_answer": "E", # Not in A, B, C, D
        "subject": "Mathematics",
        "topic": "Arithmetic",
        "subtopic": "Addition",
        "difficulty": "easy"
    }
    with pytest.raises(Exception) as exc:
        QuestionModel(**invalid_data)
    assert "Correct answer must be one of 'A', 'B', 'C', 'D'" in str(exc.value)


def test_reject_empty_question_text():
    invalid_data = {
        "id": "MATH-004",
        "question": "   ",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "correct_answer": "A",
        "subject": "Mathematics",
        "topic": "Arithmetic",
        "subtopic": "Addition",
        "difficulty": "easy"
    }
    with pytest.raises(Exception) as exc:
        QuestionModel(**invalid_data)
    assert "Question text cannot be empty" in str(exc.value)


def test_reject_verified_question_missing_explanation():
    invalid_data = {
        "id": "MATH-005",
        "question": "What is 5 x 5?",
        "options": {"A": "25", "B": "20", "C": "15", "D": "30"},
        "correct_answer": "A",
        "explanation": None, # Missing for verified!
        "subject": "Mathematics",
        "topic": "Arithmetic",
        "subtopic": "Multiplication",
        "difficulty": "easy",
        "verified": True
    }
    with pytest.raises(Exception) as exc:
        QuestionModel(**invalid_data)
    assert "Verified questions must have a non-empty explanation" in str(exc.value)


def test_unverified_question_preserved_not_falsely_verified():
    unverified_data = {
        "id": "MATH-006",
        "question": "What is 10 / 2?",
        "options": {"A": "5", "B": "2", "C": "4", "D": "1"},
        "correct_answer": "A",
        "explanation": None,
        "subject": "Mathematics",
        "topic": "Arithmetic",
        "subtopic": "Division",
        "difficulty": "easy",
        "verified": False
    }
    model = QuestionModel(**unverified_data)
    assert model.verified is False


# =====================================================================
# 2. DUPLICATE DETECTION TESTS
# =====================================================================

def test_exact_duplicate_detection():
    q_text = "What is the capital of Gujarat?"
    opts = {"A": "Gandhinagar", "B": "Ahmedabad", "C": "Surat", "D": "Vadodara"}
    hash1 = compute_question_hash(q_text, opts)
    # Slight whitespace / casing variation in question
    q_text_var = "  what is the CAPITAL of gujarat? "
    hash2 = compute_question_hash(q_text_var, opts)
    assert hash1 == hash2


def test_probable_duplicate_detection():
    text1 = "Find the eigenvalues of a 2x2 symmetric matrix"
    text2 = "Calculate the eigenvalues of a 2x2 symmetric matrix"
    sim = calculate_similarity(text1, text2)
    assert sim >= 0.80


# =====================================================================
# 3. IMPORT / EXPORT SYSTEM TESTS
# =====================================================================

def test_import_json_and_preview_workflow():
    payload = [
        {
            "id": "IMP-001",
            "question": "What is log(1) to any base?",
            "options": {"A": "0", "B": "1", "C": "e", "D": "undefined"},
            "correct_answer": "A",
            "explanation": "log(1) is always 0.",
            "subject": "Mathematics",
            "topic": "Logarithms",
            "subtopic": "Properties",
            "difficulty": "easy",
            "verified": True
        },
        {
            "id": "IMP-002",
            "question": "What is log(e) to base e?",
            "options": {"A": "1", "B": "0", "C": "e", "D": "2"},
            "correct_answer": "A",
            "explanation": "log_a(a) = 1.",
            "subject": "Mathematics",
            "topic": "Logarithms",
            "subtopic": "Properties",
            "difficulty": "easy",
            "verified": True
        }
    ]
    raw_bytes = json.dumps(payload).encode("utf-8")

    # Step 1: Preview mode (does not commit)
    prev = process_import(raw_bytes, "test.json", preview_only=True)
    assert prev["total_read"] == 2
    assert prev["valid_count"] == 2
    assert prev["imported"] == 0

    with get_db() as conn:
        cnt = conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
        assert cnt == 0

    # Step 2: Commit mode
    res = process_import(raw_bytes, "test.json", preview_only=False)
    assert res["imported"] == 2

    with get_db() as conn:
        cnt = conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
        assert cnt == 2


def test_import_exact_duplicate_rejected():
    item = {
        "id": "DUP-001",
        "question": "Is copper a conductor or insulator?",
        "options": {"A": "Conductor", "B": "Insulator", "C": "Semiconductor", "D": "Superconductor"},
        "correct_answer": "A",
        "explanation": "Copper has free valence electrons and conducts electricity.",
        "subject": "Physics",
        "topic": "Electricity",
        "subtopic": "Conductors",
        "difficulty": "easy",
        "verified": True
    }
    raw = json.dumps([item]).encode("utf-8")
    # First import: success
    res1 = process_import(raw, "dup.json", preview_only=False)
    assert res1["imported"] == 1

    # Second import with same content (even with different ID)
    item2 = dict(item)
    item2["id"] = "DUP-002"
    raw2 = json.dumps([item2]).encode("utf-8")
    res2 = process_import(raw2, "dup2.json", preview_only=False)
    assert res2["exact_duplicates_count"] == 1
    assert res2["imported"] == 0


def test_quarantined_record_export():
    invalid_item = {
        "id": "BAD-001",
        "question": "", # Invalid empty question
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "correct_answer": "A",
        "subject": "Science",
        "topic": "General",
        "subtopic": "Units",
        "difficulty": "easy"
    }
    raw = json.dumps([invalid_item]).encode("utf-8")
    res = process_import(raw, "bad.json", preview_only=False)
    assert res["rejected_count"] == 1

    quarantined = export_quarantined_records()
    assert len(quarantined) >= 1
    assert "Question text cannot be empty" in quarantined[0]["reason"]


# =====================================================================
# 4. ADAPTIVE PRIORITY & DIAGNOSTIC MODE TESTS
# =====================================================================

def test_adaptive_priority_and_diagnostic():
    # Insert two topics
    with get_db() as conn:
        sub_id, top1_id, st1_id = get_or_create_hierarchy(conn, "Math", "Calculus", "Limits")
        sub_id, top2_id, st2_id = get_or_create_hierarchy(conn, "Math", "Algebra", "Polynomials")

        # Insert question for top1
        opts = {"A": "1", "B": "2", "C": "3", "D": "4"}
        h1 = compute_question_hash("Limit q1", opts)
        conn.execute(
            """
            INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                   correct_answer, explanation, subject_id, topic_id, subtopic_id,
                                   difficulty, verified, text_hash, created_at)
            VALUES ('Q-T1', 'Limit q1', '1', '2', '3', '4', 'A', 'Expl', ?, ?, ?, 'easy', 1, ?, datetime('now'))
            """, (sub_id, top1_id, st1_id, h1)
        )
        # Record incorrect attempt on Calculus
        conn.execute(
            """
            INSERT INTO sessions (id, session_type, total_questions, started_at)
            VALUES ('SESS-TEST', 'daily_mixed', 1, datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO attempts (question_id, session_id, selected_option, is_correct, time_spent_seconds, attempted_at)
            VALUES ('Q-T1', 'SESS-TEST', 'B', 0, 30, datetime('now'))
            """
        )

    priorities = calculate_adaptive_priorities()
    assert len(priorities) == 2

    # Topic with wrong attempt should have higher priority than untouched topic
    top1_p = next(p for p in priorities if p["topic_name"] == "Calculus")
    top2_p = next(p for p in priorities if p["topic_name"] == "Algebra")

    # Algebra has 0 attempts -> flagged as diagnostic
    assert top2_p["is_diagnostic"] is True
    assert "diagnostic" in top2_p["explanation"].lower()
    # Calculus has recent wrong attempt -> higher weakness score
    assert top1_p["components"]["weakness_score"] > 0.5


# =====================================================================
# 5. PRACTICE SESSION & QUESTION SELECTION TESTS
# =====================================================================

def test_session_creation_no_intra_session_duplicates():
    # Seed 5 verified questions
    with get_db() as conn:
        sub_id, top_id, st_id = get_or_create_hierarchy(conn, "Eng", "Electrical", "AC")
        for i in range(1, 6):
            qid = f"ELEC-{i}"
            opts = {"A": f"A{i}", "B": f"B{i}", "C": f"C{i}", "D": f"D{i}"}
            h = compute_question_hash(f"Question text {i}", opts)
            conn.execute(
                """
                INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                       correct_answer, explanation, subject_id, topic_id, subtopic_id,
                                       difficulty, verified, text_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'A', 'Verified explanation', ?, ?, ?, 'medium', 1, ?, datetime('now'))
                """, (qid, f"Question text {i}", f"A{i}", f"B{i}", f"C{i}", f"D{i}", sub_id, top_id, st_id, h)
            )

    sess = create_practice_session(session_type="daily_mixed", size=4)
    q_ids = [q["question_id"] for q in sess["questions"]]
    # Ensure exactly 4 questions and no duplicates
    assert len(q_ids) == 4
    assert len(set(q_ids)) == 4


# =====================================================================
# 6. REVISION SCHEDULING (SPACED REPETITION) TESTS
# =====================================================================

def test_spaced_repetition_intervals():
    with get_db() as conn:
        sub_id, top_id, st_id = get_or_create_hierarchy(conn, "Math", "Trig", "Identities")
        opts = {"A": "1", "B": "0", "C": "-1", "D": "2"}
        h = compute_question_hash("cos^2(x) + sin^2(x)", opts)
        conn.execute(
            """
            INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                   correct_answer, explanation, subject_id, topic_id, subtopic_id,
                                   difficulty, verified, text_hash, created_at)
            VALUES ('TRIG-001', 'cos^2(x) + sin^2(x)', '1', '0', '-1', '2', 'A', 'Identity = 1', ?, ?, ?, 'easy', 1, ?, datetime('now'))
            """, (sub_id, top_id, st_id, h)
        )

        # 1. Correct attempt with high confidence -> scheduled in 7 days
        res1 = update_spaced_repetition(conn, 'TRIG-001', is_correct=True, confidence='high')
        assert res1["interval_days"] == 7

        # 2. Subsequent incorrect attempt -> interval resets to 1 day
        res2 = update_spaced_repetition(conn, 'TRIG-001', is_correct=False, mistake_category='formula')
        assert res2["interval_days"] == 1
        assert res2["mistake_category"] == 'formula'


# =====================================================================
# 7. SCORING & NEGATIVE MARKING TESTS
# =====================================================================

def test_marking_scheme_and_mock_exam():
    with get_db() as conn:
        sub_id, top_id, st_id = get_or_create_hierarchy(conn, "Math", "Trig", "Formulas")
        for i in range(1, 4):
            qid = f"MARK-{i}"
            opts = {"A": "Correct", "B": "Wrong1", "C": "Wrong2", "D": "Wrong3"}
            h = compute_question_hash(f"Marking Q {i}", opts)
            conn.execute(
                """
                INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                       correct_answer, explanation, subject_id, topic_id, subtopic_id,
                                       difficulty, verified, text_hash, created_at)
                VALUES (?, ?, 'Correct', 'Wrong1', 'Wrong2', 'Wrong3', 'A', 'Expl', ?, ?, ?, 'easy', 1, ?, datetime('now'))
                """, (qid, f"Marking Q {i}", sub_id, top_id, st_id, h)
            )

    sess = create_practice_session(session_type="full_mock", size=3)
    sess_id = sess["session_id"]

    # In mock exam, answers must be hidden while active
    assert sess["questions"][0]["correct_answer"] is None
    assert sess["questions"][0]["explanation"] is None

    with get_db() as conn:
        q1_corr = conn.execute("SELECT shuffled_correct FROM session_questions WHERE session_id = ? AND question_id = 'MARK-1'", (sess_id,)).fetchone()[0]
        q2_corr = conn.execute("SELECT shuffled_correct FROM session_questions WHERE session_id = ? AND question_id = 'MARK-2'", (sess_id,)).fetchone()[0]
    q2_wrong = [k for k in ["A", "B", "C", "D"] if k != q2_corr][0]

    # Answer Q1 correctly, Q2 incorrectly, Q3 unanswered
    record_question_answer(sess_id, "MARK-1", selected_option=q1_corr, time_spent_seconds=20)
    record_question_answer(sess_id, "MARK-2", selected_option=q2_wrong, time_spent_seconds=25)
    # Q3 left unanswered

    summary = complete_session(sess_id, time_taken_seconds=45)
    # Correct = 1 (+1.0), Incorrect = 1 (-0.25), Unanswered = 1 (0.0) -> Score = 0.75
    assert summary["correct_count"] == 1
    assert summary["incorrect_count"] == 1
    assert summary["unanswered_count"] == 1
    assert summary["total_score"] == 0.75
    assert summary["accuracy_pct"] == 50.0


# =====================================================================
# 8. BACKUP AND RESTORE TESTS
# =====================================================================

def test_database_backup_and_restore():
    # Insert test record
    with get_db() as conn:
        sub_id, top_id, st_id = get_or_create_hierarchy(conn, "General", "Test", "Sub")
        opts = {"A": "1", "B": "2", "C": "3", "D": "4"}
        h = compute_question_hash("Backup test question", opts)
        conn.execute(
            """
            INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                   correct_answer, explanation, subject_id, topic_id, subtopic_id,
                                   difficulty, verified, text_hash, created_at)
            VALUES ('BKP-001', 'Backup test question', '1', '2', '3', '4', 'A', 'Expl', ?, ?, ?, 'easy', 1, ?, datetime('now'))
            """, (sub_id, top_id, st_id, h)
        )

    # Create backup
    backup_path = create_backup("test")
    assert os.path.exists(backup_path)

    # Modify primary DB
    with get_db() as conn:
        conn.execute("DELETE FROM questions WHERE id = 'BKP-001'")
        cnt = conn.execute("SELECT COUNT(*) as c FROM questions WHERE id = 'BKP-001'").fetchone()["c"]
        assert cnt == 0

    # Restore from backup
    restore_backup(backup_path)

    # Verify restored
    with get_db() as conn:
        cnt = conn.execute("SELECT COUNT(*) as c FROM questions WHERE id = 'BKP-001'").fetchone()["c"]
        assert cnt == 1


# =====================================================================
# 9. MARKDOWN (.MD) MATH PARSING & IMPORT/EXPORT TESTS
# =====================================================================

def test_markdown_math_question_parsing():
    from services.markdown_parser import parse_markdown_questions

    sample_md = """# Sample Maths Question Bank

---
## Question: MD-TEST-001
**Subject**: Mathematics
**Topic**: Calculus
**Subtopic**: Definite Integrals
**Difficulty**: medium
**Verified**: true

Evaluate the integral:
$$\\int_0^1 x^2 \\, dx$$

- (A) $\\frac{1}{3}$
- (B) $\\frac{1}{2}$
- (C) $1$
- (D) $0$

**Correct Answer**: A
**Explanation**:
$$\\int_0^1 x^2 \\, dx = \\left[ \\frac{x^3}{3} \\right]_0^1 = \\frac{1}{3}$$
"""
    records = parse_markdown_questions(sample_md)
    assert len(records) == 1
    q = records[0]
    assert q["id"] == "MD-TEST-001"
    assert "\\int_0^1 x^2" in q["question"]
    assert q["options"]["A"] == "$\\frac{1}{3}$"
    assert q["correct_answer"] == "A"
    assert q["subject"] == "Mathematics"
    assert "x^3" in q["explanation"]


def test_markdown_file_import_and_export():
    sample_md = """---
## Question: MD-EXP-001
**Subject**: Mathematics
**Topic**: Linear Algebra
**Subtopic**: Matrices
**Difficulty**: easy
**Verified**: true

What is the determinant of matrix $\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$?

- (A) $-2$
- (B) $2$
- (C) $10$
- (D) $0$

**Correct Answer**: A
**Explanation**:
$$\\det = (1)(4) - (2)(3) = 4 - 6 = -2$$
"""
    raw_bytes = sample_md.encode("utf-8")
    res = process_import(raw_bytes, "test_math.md", preview_only=False)
    assert res["imported"] == 1

    # Verify question in DB
    with get_db() as conn:
        row = conn.execute("SELECT * FROM questions WHERE id = 'MD-EXP-001'").fetchone()
        assert row is not None
        assert row["correct_answer"] == "A"

    # Verify export to .md format
    exported_bytes, filename, media_type = export_questions(format_type="md")
    assert filename.endswith(".md")
    assert media_type == "text/markdown"
    exported_text = exported_bytes.decode("utf-8")
    assert "MD-EXP-001" in exported_text
    assert "Linear Algebra" in exported_text

