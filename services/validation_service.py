import json
from typing import Dict, Any, Tuple, Optional, List
import sqlite3
from models.schemas import QuestionModel, QuestionSource
from services.duplicate_service import compute_question_hash, check_exact_duplicate, check_duplicate_fast, find_probable_duplicates


def get_or_create_hierarchy(
    conn: sqlite3.Connection,
    subject_name: str,
    topic_name: str,
    subtopic_name: str
) -> Tuple[int, int, int]:
    """Ensures subject, topic, and subtopic exist in relational tables and returns their IDs."""
    sub_clean = subject_name.strip()
    top_clean = topic_name.strip()
    subtop_clean = subtopic_name.strip()

    # Subject
    row = conn.execute("SELECT id FROM subjects WHERE name = ? COLLATE NOCASE", (sub_clean,)).fetchone()
    if row:
        subject_id = row["id"]
    else:
        cur = conn.execute("INSERT INTO subjects (name) VALUES (?)", (sub_clean,))
        subject_id = cur.lastrowid

    # Topic
    row = conn.execute(
        "SELECT id FROM topics WHERE subject_id = ? AND name = ? COLLATE NOCASE",
        (subject_id, top_clean)
    ).fetchone()
    if row:
        topic_id = row["id"]
    else:
        cur = conn.execute(
            "INSERT INTO topics (subject_id, name) VALUES (?, ?)",
            (subject_id, top_clean)
        )
        topic_id = cur.lastrowid

    # Subtopic
    row = conn.execute(
        "SELECT id FROM subtopics WHERE topic_id = ? AND name = ? COLLATE NOCASE",
        (topic_id, subtop_clean)
    ).fetchone()
    if row:
        subtopic_id = row["id"]
    else:
        cur = conn.execute(
            "INSERT INTO subtopics (topic_id, name) VALUES (?, ?)",
            (topic_id, subtop_clean)
        )
        subtopic_id = cur.lastrowid

    return subject_id, topic_id, subtopic_id


def validate_and_prepare_question(
    raw_data: Dict[str, Any],
    conn: sqlite3.Connection,
    check_duplicates: bool = True
) -> Tuple[Optional[QuestionModel], Optional[str], Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates a raw dictionary against QuestionModel requirements.
    Returns: (QuestionModel or None, error_message or None, exact_duplicate_info or None, probable_duplicates list)
    """
    try:
        # Handle stringified options if coming from CSV or flat Excel
        if "options" in raw_data and isinstance(raw_data["options"], str):
            try:
                raw_data["options"] = json.loads(raw_data["options"])
            except Exception:
                pass
        
        # If options are flattened (Option A, Option B, etc.)
        if "options" not in raw_data or not isinstance(raw_data.get("options"), dict):
            opts = {}
            for key in ["A", "B", "C", "D"]:
                alt_keys = [f"option_{key.lower()}", f"option_{key}", f"option{key.lower()}", f"option{key}", f"Option {key}", f"Option_{key}"]
                for ak in alt_keys:
                    if ak in raw_data and raw_data[ak] is not None:
                        opts[key] = str(raw_data[ak])
                        break
            if len(opts) == 4:
                raw_data["options"] = opts

        # Source handling
        if "source" in raw_data and isinstance(raw_data["source"], str):
            try:
                raw_data["source"] = json.loads(raw_data["source"])
            except Exception:
                raw_data["source"] = {"name": raw_data["source"]}

        # Tags handling
        if "tags" in raw_data and isinstance(raw_data["tags"], str):
            try:
                raw_data["tags"] = json.loads(raw_data["tags"])
            except Exception:
                raw_data["tags"] = [t.strip() for t in raw_data["tags"].split(",") if t.strip()]

        # Verified boolean normalization
        if "verified" in raw_data:
            if isinstance(raw_data["verified"], str):
                raw_data["verified"] = raw_data["verified"].strip().lower() in ["true", "1", "yes"]
            else:
                raw_data["verified"] = bool(raw_data["verified"])

        # Pydantic validation
        model = QuestionModel(**raw_data)

        # Check duplicates using O(1) indexed lookups (scale-ready for 1,000,000+ questions)
        if check_duplicates and conn:
            dup_info = check_duplicate_fast(conn, model.id, model.question, model.options)
            if dup_info:
                return None, dup_info["reason"], dup_info, []

        return model, None, None, []

    except Exception as e:
        return None, str(e), None, []
