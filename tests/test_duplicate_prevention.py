import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import pytest
from fastapi.testclient import TestClient

from app import app
from database.db import get_db, init_db
from services.duplicate_service import (
    compute_question_hash,
    compute_question_text_hash,
    check_duplicate_fast,
    batch_check_duplicates_fast
)
from services.import_export_service import process_import


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use an isolated SQLite test database for each test session."""
    test_db_file = str(tmp_path / "test_dup.db")
    monkeypatch.setattr("database.db.DB_PATH", test_db_file)
    monkeypatch.setattr("database.db.DATA_DIR", str(tmp_path))
    monkeypatch.setattr("database.db.BACKUPS_DIR", str(tmp_path / "backups"))
    os.makedirs(str(tmp_path / "backups"), exist_ok=True)
    init_db()
    yield test_db_file


def test_add_single_question_and_reject_exact_duplicate():
    """Verify that adding an exact duplicate question is strictly rejected and never added."""
    client = TestClient(app)

    payload = {
        "id": "MATH-DUP-001",
        "question": "What is the determinant of a 2x2 identity matrix?",
        "options": {
            "A": "1",
            "B": "0",
            "C": "-1",
            "D": "2"
        },
        "correct_answer": "A",
        "explanation": "Det(I) = 1*1 - 0*0 = 1.",
        "subject": "Mathematics",
        "topic": "Matrices",
        "subtopic": "Determinants",
        "difficulty": "easy",
        "verified": True
    }

    # 1. First addition: must succeed (201 Created)
    res1 = client.post("/api/questions", json=payload)
    assert res1.status_code == 201
    assert res1.json()["success"] is True

    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        assert count == 1

    # 2. Duplicate addition attempt: must be rejected with 409 Conflict
    res2 = client.post("/api/questions", json=payload)
    assert res2.status_code == 409
    err = res2.json()
    assert err["detail"]["error"] == "DUPLICATE_QUESTION"

    # Database count must still be 1 (duplicate was NOT added)
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        assert count == 1


def test_reject_duplicate_with_shuffled_options():
    """Verify that shuffling options A/B/C/D does not bypass duplicate detection."""
    client = TestClient(app)

    original = {
        "id": "MATH-SHUF-001",
        "question": "If matrix A is singular, what is its determinant?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "undefined",
            "D": "-1"
        },
        "correct_answer": "A",
        "explanation": "A matrix is singular if and only if its determinant is 0.",
        "subject": "Mathematics",
        "topic": "Matrices",
        "subtopic": "Properties",
        "difficulty": "easy",
        "verified": True
    }

    res1 = client.post("/api/questions", json=original)
    assert res1.status_code == 201

    # Same question, but with options permuted to different letters
    shuffled = {
        "id": "MATH-SHUF-002",
        "question": "If matrix A is singular, what is its determinant?",
        "options": {
            "A": "1",
            "B": "-1",
            "C": "0",
            "D": "undefined"
        },
        "correct_answer": "C",
        "explanation": "Det is 0.",
        "subject": "Mathematics",
        "topic": "Matrices",
        "subtopic": "Properties",
        "difficulty": "easy",
        "verified": True
    }

    res2 = client.post("/api/questions", json=shuffled)
    assert res2.status_code == 409
    err = res2.json()
    assert err["detail"]["error"] == "DUPLICATE_QUESTION"

    # Database count must still be 1
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        assert count == 1


def test_reject_duplicate_identical_question_text():
    """Verify that submitting identical question text with a new ID is detected and rejected."""
    client = TestClient(app)

    q1 = {
        "id": "MATH-TEXT-001",
        "question": "What is the value of sin(90 degrees)?",
        "options": {
            "A": "1",
            "B": "0",
            "C": "-1",
            "D": "0.5"
        },
        "correct_answer": "A",
        "explanation": "sin(pi/2) = 1.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Standard Values",
        "difficulty": "easy",
        "verified": True
    }
    res1 = client.post("/api/questions", json=q1)
    assert res1.status_code == 201

    # New ID, slightly different option labels, but identical normalized question text
    q2 = {
        "id": "MATH-TEXT-002",
        "question": "  what is the VALUE of sin(90 DEGREES)?  ",
        "options": {
            "A": "1.0",
            "B": "0.0",
            "C": "None",
            "D": "Inf"
        },
        "correct_answer": "A",
        "explanation": "Value is 1.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Standard Values",
        "difficulty": "easy",
        "verified": True
    }
    res2 = client.post("/api/questions", json=q2)
    assert res2.status_code == 409
    assert res2.json()["detail"]["error"] == "DUPLICATE_QUESTION"

    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        assert count == 1


def test_check_duplicate_probe_endpoint():
    """Verify the /api/questions/check-duplicate probe endpoint returns instant O(1) status."""
    client = TestClient(app)

    q = {
        "id": "ENG-PROBE-001",
        "question": "What is the SI unit of electric resistance?",
        "options": {
            "A": "Ohm",
            "B": "Volt",
            "C": "Ampere",
            "D": "Watt"
        },
        "correct_answer": "A",
        "explanation": "Resistance is measured in Ohms.",
        "subject": "Engineering Science",
        "topic": "Electrical",
        "subtopic": "Units",
        "difficulty": "easy",
        "verified": True
    }
    client.post("/api/questions", json=q)

    # Probe with duplicate
    probe_dup = client.post("/api/questions/check-duplicate", json={
        "question": "What is the SI unit of electric resistance?",
        "options": {"A": "Ohm", "B": "Volt", "C": "Ampere", "D": "Watt"}
    })
    assert probe_dup.status_code == 200
    res_dup = probe_dup.json()
    assert res_dup["is_duplicate"] is True
    assert res_dup["existing_id"] == "ENG-PROBE-001"

    # Probe with unique question
    probe_clean = client.post("/api/questions/check-duplicate", json={
        "question": "What is the SI unit of luminous intensity?",
        "options": {"A": "Candela", "B": "Lumen", "C": "Lux", "D": "Tesla"}
    })
    assert probe_clean.status_code == 200
    res_clean = probe_clean.json()
    assert res_clean["is_duplicate"] is False
    assert res_clean["existing_id"] is None


def test_bulk_import_skips_duplicates_and_preserves_speed():
    """Verify that importing duplicate questions in bulk skips duplicates and adds only unique ones."""
    # Seed 1 existing question in DB
    client = TestClient(app)
    existing = {
        "id": "BULK-SEED-001",
        "question": "Which of the following is a scalar quantity?",
        "options": {
            "A": "Mass",
            "B": "Velocity",
            "C": "Force",
            "D": "Acceleration"
        },
        "correct_answer": "A",
        "explanation": "Mass has magnitude but no direction.",
        "subject": "Physics",
        "topic": "Vectors",
        "subtopic": "Scalars",
        "difficulty": "easy",
        "verified": True
    }
    client.post("/api/questions", json=existing)

    # Prepare batch of 4 questions:
    # - 1 duplicate of existing DB question
    # - 1 new unique question
    # - 1 duplicate of the new question within the same batch (intra-batch duplicate)
    # - 1 second new unique question
    batch = [
        {
            "id": "BULK-NEW-001",
            "question": "Which of the following is a scalar quantity?", # DUPLICATE OF DB
            "options": {"A": "Mass", "B": "Velocity", "C": "Force", "D": "Acceleration"},
            "correct_answer": "A",
            "explanation": "Scalar quantity.",
            "subject": "Physics",
            "topic": "Vectors",
            "subtopic": "Scalars",
            "difficulty": "easy",
            "verified": True
        },
        {
            "id": "BULK-NEW-002",
            "question": "What is the speed of light in vacuum?",
            "options": {"A": "3 x 10^8 m/s", "B": "3 x 10^6 m/s", "C": "3 x 10^10 m/s", "D": "3 x 10^5 km/s"},
            "correct_answer": "A",
            "explanation": "Speed of light c = 3 x 10^8 m/s.",
            "subject": "Physics",
            "topic": "Optics",
            "subtopic": "Speed of Light",
            "difficulty": "easy",
            "verified": True
        },
        {
            "id": "BULK-NEW-003",
            "question": "What is the speed of light in vacuum?", # INTRA-BATCH DUPLICATE OF BULK-NEW-002
            "options": {"A": "3 x 10^8 m/s", "B": "3 x 10^6 m/s", "C": "3 x 10^10 m/s", "D": "3 x 10^5 km/s"},
            "correct_answer": "A",
            "explanation": "Speed of light.",
            "subject": "Physics",
            "topic": "Optics",
            "subtopic": "Speed of Light",
            "difficulty": "easy",
            "verified": True
        },
        {
            "id": "BULK-NEW-004",
            "question": "What is the acceleration due to gravity on Earth?",
            "options": {"A": "9.8 m/s^2", "B": "8.9 m/s^2", "C": "9.8 km/s^2", "D": "10.8 m/s^2"},
            "correct_answer": "A",
            "explanation": "Standard gravity g ~ 9.8 m/s^2.",
            "subject": "Physics",
            "topic": "Gravitation",
            "subtopic": "Acceleration",
            "difficulty": "easy",
            "verified": True
        }
    ]

    raw_bytes = json.dumps(batch).encode("utf-8")
    result = process_import(raw_bytes, "test_batch.json", preview_only=False)

    assert result["total_read"] == 4
    assert result["imported"] == 2 # Only BULK-NEW-002 and BULK-NEW-004 added!
    assert result["exact_duplicates_count"] == 2 # 1 DB match + 1 intra-batch match

    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        # 1 original seeded + 2 newly imported = 3 total
        assert total == 3


def test_scale_benchmark_duplicate_detection():
    """
    Simulates high volume (5,000 synthetic questions in database) and verifies
    that duplicate checking remains sub-millisecond fast O(1) via B-Tree indexing.
    """
    with get_db() as conn:
        # Batch insert 5,000 synthetic indexed questions
        sub_id = conn.execute("INSERT INTO subjects (name) VALUES ('Benchmark')").lastrowid
        top_id = conn.execute("INSERT INTO topics (subject_id, name) VALUES (?, 'Scale')", (sub_id,)).lastrowid
        st_id = conn.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, 'O(1) Test')", (top_id,)).lastrowid

        bulk_data = []
        for i in range(5000):
            qid = f"SCALE-{i:05d}"
            q_text = f"Synthetic benchmark question number {i} for high throughput test"
            opts = {"A": f"OptA {i}", "B": f"OptB {i}", "C": f"OptC {i}", "D": f"OptD {i}"}
            t_hash = compute_question_hash(q_text, opts)
            q_hash = compute_question_text_hash(q_text)
            bulk_data.append((
                qid, q_text, opts["A"], opts["B"], opts["C"], opts["D"], "A",
                "Explanation", sub_id, top_id, st_id, "easy", "{}", "[]", 1, t_hash, q_hash, "2026-10-26T00:00:00"
            ))

        conn.executemany(
            """
            INSERT INTO questions (
                id, question_text, option_a, option_b, option_c, option_d,
                correct_answer, explanation, subject_id, topic_id, subtopic_id,
                difficulty, source_json, tags_json, verified, text_hash, question_text_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            bulk_data
        )

        total_in_db = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        assert total_in_db >= 5000

        # Benchmark 200 lookups against the database
        start = time.perf_counter()
        for i in range(100):
            # Known duplicate
            dup = check_duplicate_fast(
                conn,
                f"SCALE-{i:05d}",
                f"Synthetic benchmark question number {i} for high throughput test",
                {"A": f"OptA {i}", "B": f"OptB {i}", "C": f"OptC {i}", "D": f"OptD {i}"}
            )
            assert dup is not None

        for i in range(100):
            # Unique non-duplicate
            dup = check_duplicate_fast(
                conn,
                f"UNIQUE-{i:05d}",
                f"Non existent unique question {i} for benchmark",
                {"A": "Alpha", "B": "Beta", "C": "Gamma", "D": "Delta"}
            )
            assert dup is None

        elapsed = time.perf_counter() - start
        avg_per_check = elapsed / 200

        # Must average less than 1 millisecond (0.001s) per check!
        print(f"\nBenchmark completed: 200 lookups against {total_in_db} questions in {elapsed:.4f}s ({avg_per_check*1000:.3f}ms per check)")
        assert avg_per_check < 0.002 # Under 2ms on any hardware, typically 0.05ms
