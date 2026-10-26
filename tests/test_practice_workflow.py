import os
import sys
import json
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db, init_db
from services.practice_service import (
    create_practice_session,
    get_session_state,
    record_question_answer,
    complete_session
)
from services.validation_service import get_or_create_hierarchy
from services.duplicate_service import compute_question_hash


@pytest.fixture(autouse=True)
def setup_practice_test_db(tmp_path, monkeypatch):
    """Set up an isolated SQLite database with sample test questions."""
    test_db = str(tmp_path / "test_practice.db")
    monkeypatch.setattr("database.db.DB_PATH", test_db)
    monkeypatch.setattr("database.db.DATA_DIR", str(tmp_path))
    monkeypatch.setattr("database.db.BACKUPS_DIR", str(tmp_path / "backups"))
    os.makedirs(str(tmp_path / "backups"), exist_ok=True)
    init_db()

    # Seed 6 verified test questions across difficulties
    sample_questions = [
        {
            "id": "TEST-Q-01",
            "question": "What is 2 + 2?",
            "options": {"A": "4", "B": "5", "C": "6", "D": "7"},
            "correct_answer": "A",
            "explanation": "2 + 2 = 4.",
            "subject": "Mathematics",
            "topic": "Arithmetic",
            "subtopic": "Addition",
            "difficulty": "easy"
        },
        {
            "id": "TEST-Q-02",
            "question": "What is 3 * 3?",
            "options": {"A": "6", "B": "9", "C": "12", "D": "15"},
            "correct_answer": "B",
            "explanation": "3 * 3 = 9.",
            "subject": "Mathematics",
            "topic": "Arithmetic",
            "subtopic": "Multiplication",
            "difficulty": "easy"
        },
        {
            "id": "TEST-Q-03",
            "question": "Derivative of x^3?",
            "options": {"A": "x^2", "B": "3x", "C": "3x^2", "D": "6x"},
            "correct_answer": "C",
            "explanation": "d/dx(x^3) = 3x^2.",
            "subject": "Mathematics",
            "topic": "Calculus",
            "subtopic": "Differentiation",
            "difficulty": "medium"
        },
        {
            "id": "TEST-Q-04",
            "question": "Integral of 2x dx from 0 to 1?",
            "options": {"A": "0", "B": "2", "C": "0.5", "D": "1"},
            "correct_answer": "D",
            "explanation": "Integral is x^2 from 0 to 1 = 1.",
            "subject": "Mathematics",
            "topic": "Calculus",
            "subtopic": "Integration",
            "difficulty": "medium"
        },
        {
            "id": "TEST-Q-05",
            "question": "Eigenvalue of identity matrix I_2?",
            "options": {"A": "1", "B": "0", "C": "2", "D": "-1"},
            "correct_answer": "A",
            "explanation": "All eigenvalues of identity matrix are 1.",
            "subject": "Mathematics",
            "topic": "Matrices",
            "subtopic": "Eigenvalues",
            "difficulty": "hard"
        },
        {
            "id": "TEST-Q-06",
            "question": "Determinant of [[1, 2], [3, 4]]?",
            "options": {"A": "2", "B": "-2", "C": "10", "D": "-10"},
            "correct_answer": "B",
            "explanation": "1*4 - 2*3 = 4 - 6 = -2.",
            "subject": "Mathematics",
            "topic": "Matrices",
            "subtopic": "Determinants",
            "difficulty": "hard"
        }
    ]

    with get_db() as conn:
        for q in sample_questions:
            sub_id, top_id, subtop_id = get_or_create_hierarchy(conn, q["subject"], q["topic"], q["subtopic"])
            text_hash = compute_question_hash(q["question"], q["options"])
            conn.execute(
                """
                INSERT INTO questions (
                    id, question_text, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, subject_id, topic_id, subtopic_id,
                    difficulty, source_json, tags_json, verified, text_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '[]', 1, ?, datetime('now'))
                """,
                (
                    q["id"], q["question"], q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"],
                    q["correct_answer"], q["explanation"], sub_id, top_id, subtop_id,
                    q["difficulty"], text_hash
                )
            )

    yield test_db


def test_option_randomization_and_remapping():
    """Verify that practice session shuffles options while preserving the correct value."""
    session = create_practice_session(session_type="daily_mixed", size=6)
    assert session["session_id"]
    assert len(session["questions"]) == 6

    # Verify that in session_questions, the shuffled option corresponding to correct_answer matches the true value
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT sq.question_id, sq.shuffled_options, sq.shuffled_correct,
                   q.option_a, q.option_b, q.option_c, q.option_d, q.correct_answer
            FROM session_questions sq
            JOIN questions q ON sq.question_id = q.id
            WHERE sq.session_id = ?
            """,
            (session["session_id"],)
        ).fetchall()

    for r in rows:
        assert r["shuffled_options"] is not None
        assert r["shuffled_correct"] in ["A", "B", "C", "D"]

        shuffled_opts = json.loads(r["shuffled_options"])
        shuffled_corr_val = shuffled_opts[r["shuffled_correct"]]

        orig_opts = {
            "A": r["option_a"],
            "B": r["option_b"],
            "C": r["option_c"],
            "D": r["option_d"]
        }
        orig_corr_val = orig_opts[r["correct_answer"]]

        # Critical: The displayed correct option MUST equal the original correct value!
        assert shuffled_corr_val == orig_corr_val, (
            f"Question {r['question_id']}: Shuffled correct value '{shuffled_corr_val}' "
            f"does not match original correct value '{orig_corr_val}'"
        )


def test_practice_answer_checking_workflow():
    """Verify answer evaluation against the shuffled correct answer."""
    session = create_practice_session(session_type="daily_mixed", size=2)
    s_id = session["session_id"]
    q1 = session["questions"][0]

    correct_letter = q1["correct_answer"]
    wrong_letter = [k for k in ["A", "B", "C", "D"] if k != correct_letter][0]

    # Submit wrong answer
    res_wrong = record_question_answer(
        session_id=s_id,
        question_id=q1["question_id"],
        selected_option=wrong_letter,
        time_spent_seconds=10
    )
    assert res_wrong["is_correct"] is False
    assert res_wrong["selected_option"] == wrong_letter

    # Submit correct answer
    res_correct = record_question_answer(
        session_id=s_id,
        question_id=q1["question_id"],
        selected_option=correct_letter,
        time_spent_seconds=5
    )
    assert res_correct["is_correct"] is True
    assert res_correct["selected_option"] == correct_letter


def test_difficulty_filtering():
    """Verify difficulty filter in practice sessions."""
    easy_session = create_practice_session(session_type="daily_mixed", size=2, difficulty="easy")
    for q in easy_session["questions"]:
        assert q["difficulty"] == "easy"

    hard_session = create_practice_session(session_type="daily_mixed", size=2, difficulty="hard")
    for q in hard_session["questions"]:
        assert q["difficulty"] == "hard"


def test_mock_exam_hides_answers_until_completed():
    """Verify that in full_mock, correct answers and explanations are hidden during exam and revealed after."""
    mock_session = create_practice_session(session_type="full_mock", size=4)
    s_id = mock_session["session_id"]

    state_before = get_session_state(s_id)
    for q in state_before["questions"]:
        assert q["correct_answer"] is None, "Mock exam leaked correct_answer during active exam"
        assert q["explanation"] is None, "Mock exam leaked explanation during active exam"

    # Complete the session
    summary = complete_session(s_id, time_taken_seconds=120)
    assert summary["is_completed"] is True

    state_after = get_session_state(s_id)
    for q in state_after["questions"]:
        assert q["correct_answer"] in ["A", "B", "C", "D"], "Correct answer not revealed after completion"
        assert q["explanation"], "Explanation not revealed after completion"
