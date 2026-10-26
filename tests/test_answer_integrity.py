import os
import json
import sqlite3
import pytest
from collections import Counter

DB_PATH = "data/ddcet.db"
JSON_PATH = "data/data.json"


def test_data_json_answer_distribution():
    assert os.path.exists(JSON_PATH), "data/data.json does not exist"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    assert len(questions) >= 200, f"Expected at least 200 questions, got {len(questions)}"

    counter = Counter(q["correct_answer"] for q in questions)

    # Verify all four keys exist and none dominate completely (> 50%)
    for key in ["A", "B", "C", "D"]:
        assert key in counter, f"Option {key} has zero correct answers"
        # Since we balanced it evenly (25% each), each should have at least 15% and at most 35%
        ratio = counter[key] / len(questions)
        assert 0.15 <= ratio <= 0.35, f"Option {key} ratio {ratio:.2f} is out of expected balanced range (15%-35%)"


def test_all_questions_have_valid_structure():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    for q in questions:
        assert q["id"], "Question ID is empty"
        assert q["question"].strip(), f"Question {q['id']} text is empty"
        assert set(q["options"].keys()) == {"A", "B", "C", "D"}, f"Question {q['id']} options invalid keys"
        assert q["correct_answer"] in {"A", "B", "C", "D"}, f"Question {q['id']} invalid correct_answer"
        assert q["options"][q["correct_answer"]].strip(), f"Question {q['id']} correct option is empty"
        assert q["explanation"].strip(), f"Question {q['id']} explanation is empty"


def test_database_answer_distribution():
    assert os.path.exists(DB_PATH), "data/ddcet.db does not exist"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT correct_answer, COUNT(*) as cnt FROM questions GROUP BY correct_answer").fetchall()
    conn.close()

    dist = {r["correct_answer"]: r["cnt"] for r in rows}
    total = sum(dist.values())
    assert total >= 200

    for key in ["A", "B", "C", "D"]:
        assert key in dist, f"Key {key} not found in database answer distribution"
        ratio = dist[key] / total
        assert 0.15 <= ratio <= 0.35, f"Database answer key {key} ratio {ratio:.2f} not balanced"
