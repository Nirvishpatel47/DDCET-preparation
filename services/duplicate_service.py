import re
import hashlib
from difflib import SequenceMatcher
from typing import Tuple, List, Dict, Any, Optional
import sqlite3


def normalize_text(text: str) -> str:
    """Normalizes text by lowercasing, stripping punctuation and extra whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_question_hash(question_text: str, options: Dict[str, str]) -> str:
    """
    Computes a deterministic SHA-256 hash from normalized question text
    and normalized sorted options to detect exact duplicates.
    """
    norm_q = normalize_text(question_text)
    norm_opts = []
    for k in sorted(options.keys()):
        norm_opts.append(f"{k}:{normalize_text(str(options[k]))}")
    payload = f"{norm_q}|{'|'.join(norm_opts)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculates non-LLM text similarity using SequenceMatcher ratio."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    if norm1 == norm2:
        return 1.0
    if not norm1 or not norm2:
        return 0.0
    return SequenceMatcher(None, norm1, norm2).ratio()


def check_exact_duplicate(conn: sqlite3.Connection, text_hash: str, question_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Checks if an exact duplicate question exists in the database."""
    query = "SELECT id, question_text, subject_id, topic_id FROM questions WHERE text_hash = ?"
    params = [text_hash]
    if question_id:
        query += " AND id != ?"
        params.append(question_id)
    
    row = conn.execute(query, params).fetchone()
    if row:
        return {
            "id": row["id"],
            "question_text": row["question_text"],
            "reason": "Exact match for question text and all options."
        }
    return None


def find_probable_duplicates(
    conn: sqlite3.Connection,
    question_text: str,
    subject_id: Optional[int] = None,
    threshold: float = 0.82
) -> List[Dict[str, Any]]:
    """
    Scans questions within the same subject (or recent questions) to flag probable duplicates.
    Uses offline Levenshtein/difflib token similarity. Does NOT silently delete.
    """
    norm_incoming = normalize_text(question_text)
    if len(norm_incoming) < 15:
        # Very short text, use exact threshold
        threshold = 0.90

    query = "SELECT id, question_text FROM questions"
    params = []
    if subject_id:
        query += " WHERE subject_id = ?"
        params.append(subject_id)
    
    rows = conn.execute(query, params).fetchall()
    matches = []
    for r in rows:
        sim = calculate_similarity(question_text, r["question_text"])
        if sim >= threshold:
            matches.append({
                "existing_id": r["id"],
                "existing_text": r["question_text"],
                "similarity_score": round(sim, 3),
                "reason": f"Question text is {int(sim*100)}% similar to existing question."
            })
    return matches
