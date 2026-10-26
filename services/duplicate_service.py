import re
import hashlib
from difflib import SequenceMatcher
from typing import Tuple, List, Dict, Any, Optional, Set
import sqlite3


def normalize_text(text: str) -> str:
    """
    Normalizes text by lowercasing, stripping punctuation, LaTeX delimiters, and extra whitespace.
    This guarantees that variations in spacing, casing, and LaTeX math formatting
    (e.g., '$x^2$' vs 'x^2' vs '  X^2  ') resolve to the same normalized text.
    """
    if not text:
        return ""
    text = text.lower()
    # Strip common LaTeX/markdown delimiters and formatting symbols
    text = re.sub(r"[\$\*\_\`\#\\]", " ", text)
    # Strip non-alphanumeric characters but preserve whitespace
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse multiple whitespace characters into single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_question_text_hash(question_text: str) -> str:
    """Computes a deterministic SHA-256 hash of normalized question text alone."""
    norm_q = normalize_text(question_text)
    return hashlib.sha256(norm_q.encode("utf-8")).hexdigest()


def compute_question_hash(question_text: str, options: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash from normalized question text
    and normalized sorted option VALUES (making it invariant to option shuffling)
    to detect exact duplicates.
    """
    norm_q = normalize_text(question_text)
    # Sort option values so that swapping option letters (e.g. A <-> B) does not evade duplicate detection
    norm_opts = sorted([normalize_text(str(v)) for v in options.values()])
    payload = f"{norm_q}|{'|'.join(norm_opts)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def check_exact_duplicate(
    conn: sqlite3.Connection,
    text_hash: str,
    question_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Checks if an exact duplicate question exists in the database using the indexed text_hash."""
    query = "SELECT id, question_text, subject_id, topic_id FROM questions WHERE text_hash = ?"
    params: List[Any] = [text_hash]
    if question_id:
        query += " AND id != ?"
        params.append(question_id)
    
    row = conn.execute(query, params).fetchone()
    if row:
        return {
            "id": row["id"],
            "existing_id": row["id"],
            "question_text": row["question_text"],
            "existing_text": row["question_text"],
            "reason": f"Exact match for question text and options (matches existing ID: {row['id']})."
        }
    return None


def check_duplicate_fast(
    conn: sqlite3.Connection,
    question_id: Optional[str],
    question_text: str,
    options: Optional[Dict[str, Any]] = None,
    exclude_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Lightning-fast O(1) multi-tiered duplicate check using SQLite B-Tree indexes.
    Scale-ready for 1,000,000+ questions.
    Checks in sequence:
    1. Question ID collision (B-Tree Primary Key index)
    2. Exact Question + Options collision (B-Tree idx_questions_text_hash)
    3. Normalized Question Text collision (B-Tree idx_questions_q_text_hash)
    """
    # 1. ID check
    if question_id:
        qid_clean = str(question_id).strip()
        id_query = "SELECT id, question_text FROM questions WHERE id = ?"
        id_params: List[Any] = [qid_clean]
        if exclude_id:
            id_query += " AND id != ?"
            id_params.append(exclude_id)
        row = conn.execute(id_query, id_params).fetchone()
        if row:
            return {
                "id": row["id"],
                "existing_id": row["id"],
                "existing_text": row["question_text"],
                "match_type": "id_collision",
                "reason": f"Question ID '{qid_clean}' already exists in database."
            }

    # 2. Exact Question + Options collision
    if options and isinstance(options, dict) and len(options) == 4:
        text_hash = compute_question_hash(question_text, options)
        hash_query = "SELECT id, question_text FROM questions WHERE text_hash = ?"
        hash_params: List[Any] = [text_hash]
        if exclude_id:
            hash_query += " AND id != ?"
            hash_params.append(exclude_id)
        elif question_id:
            hash_query += " AND id != ?"
            hash_params.append(question_id)
        row = conn.execute(hash_query, hash_params).fetchone()
        if row:
            return {
                "id": row["id"],
                "existing_id": row["id"],
                "existing_text": row["question_text"],
                "match_type": "exact_question_and_options",
                "reason": f"Identical question and options already exist (matches ID: {row['id']})."
            }

    # 3. Normalized Question Text collision
    q_text_hash = compute_question_text_hash(question_text)
    q_query = "SELECT id, question_text FROM questions WHERE question_text_hash = ?"
    q_params: List[Any] = [q_text_hash]
    if exclude_id:
        q_query += " AND id != ?"
        q_params.append(exclude_id)
    elif question_id:
        q_query += " AND id != ?"
        q_params.append(question_id)
    row = conn.execute(q_query, q_params).fetchone()
    if row:
        return {
            "id": row["id"],
            "existing_id": row["id"],
            "existing_text": row["question_text"],
            "match_type": "identical_question_text",
            "reason": f"Question text already exists in database (matches ID: {row['id']})."
        }

    return None


def batch_check_duplicates_fast(
    conn: sqlite3.Connection,
    records: List[Dict[str, Any]],
    chunk_size: int = 500
) -> Dict[str, Any]:
    """
    Performs ultra-fast chunked duplicate verification for bulk question imports.
    Scales smoothly even if database contains 1,000,000+ questions.
    Returns:
    {
        "duplicates_by_index": {row_index: duplicate_info_dict},
        "clean_indices": [row_index, ...]
    }
    """
    duplicates_by_index: Dict[int, Dict[str, Any]] = {}
    seen_batch_ids: Set[str] = set()
    seen_batch_hashes: Set[str] = set()
    seen_batch_q_hashes: Set[str] = set()

    # Pre-extract hashes and check intra-batch duplicates in memory O(1)
    extracted = []
    for idx, r in enumerate(records):
        qid = str(r.get("id", "")).strip() if r.get("id") else None
        q_text = str(r.get("question", "") or r.get("question_text", "")).strip()
        opts = r.get("options")

        # Intra-batch ID duplicate
        if qid:
            if qid in seen_batch_ids:
                duplicates_by_index[idx] = {
                    "id": qid,
                    "reason": f"Duplicate question ID '{qid}' found within the import file itself.",
                    "match_type": "intra_batch_id"
                }
                continue
            seen_batch_ids.add(qid)

        if not q_text:
            continue

        q_hash = compute_question_text_hash(q_text)
        if q_hash in seen_batch_q_hashes:
            duplicates_by_index[idx] = {
                "id": qid or f"Row {idx+1}",
                "reason": "Duplicate question text found within this same import file.",
                "match_type": "intra_batch_text"
            }
            continue
        seen_batch_q_hashes.add(q_hash)

        t_hash = None
        if isinstance(opts, dict) and len(opts) == 4:
            t_hash = compute_question_hash(q_text, opts)
            if t_hash in seen_batch_hashes:
                duplicates_by_index[idx] = {
                    "id": qid or f"Row {idx+1}",
                    "reason": "Identical question and options found within this same import file.",
                    "match_type": "intra_batch_exact"
                }
                continue
            seen_batch_hashes.add(t_hash)

        extracted.append((idx, qid, t_hash, q_hash, q_text))

    # Fast indexed batch lookup in SQLite (chunks of chunk_size)
    for i in range(0, len(extracted), chunk_size):
        chunk = extracted[i:i + chunk_size]
        
        # 1. Check IDs
        chunk_ids = [item[1] for item in chunk if item[1]]
        if chunk_ids:
            placeholders = ",".join(["?"] * len(chunk_ids))
            rows = conn.execute(
                f"SELECT id, question_text FROM questions WHERE id IN ({placeholders})",
                chunk_ids
            ).fetchall()
            id_map = {r["id"]: r["question_text"] for r in rows}
            for item in chunk:
                idx, qid = item[0], item[1]
                if qid and qid in id_map and idx not in duplicates_by_index:
                    duplicates_by_index[idx] = {
                        "id": qid,
                        "existing_id": qid,
                        "existing_text": id_map[qid],
                        "match_type": "id_collision",
                        "reason": f"Question ID '{qid}' already exists in database."
                    }

        # 2. Check text_hashes
        chunk_t_hashes = [item[2] for item in chunk if item[2] and item[0] not in duplicates_by_index]
        if chunk_t_hashes:
            placeholders = ",".join(["?"] * len(chunk_t_hashes))
            rows = conn.execute(
                f"SELECT id, text_hash, question_text FROM questions WHERE text_hash IN ({placeholders})",
                chunk_t_hashes
            ).fetchall()
            t_map = {r["text_hash"]: (r["id"], r["question_text"]) for r in rows}
            for item in chunk:
                idx, t_hash = item[0], item[2]
                if t_hash and t_hash in t_map and idx not in duplicates_by_index:
                    match_id, match_text = t_map[t_hash]
                    duplicates_by_index[idx] = {
                        "id": item[1] or match_id,
                        "existing_id": match_id,
                        "existing_text": match_text,
                        "match_type": "exact_question_and_options",
                        "reason": f"Identical question and options already exist (matches ID: {match_id})."
                    }

        # 3. Check question_text_hashes
        chunk_q_hashes = [item[3] for item in chunk if item[3] and item[0] not in duplicates_by_index]
        if chunk_q_hashes:
            placeholders = ",".join(["?"] * len(chunk_q_hashes))
            rows = conn.execute(
                f"SELECT id, question_text_hash, question_text FROM questions WHERE question_text_hash IN ({placeholders})",
                chunk_q_hashes
            ).fetchall()
            q_map = {r["question_text_hash"]: (r["id"], r["question_text"]) for r in rows}
            for item in chunk:
                idx, q_hash = item[0], item[3]
                if q_hash and q_hash in q_map and idx not in duplicates_by_index:
                    match_id, match_text = q_map[q_hash]
                    duplicates_by_index[idx] = {
                        "id": item[1] or match_id,
                        "existing_id": match_id,
                        "existing_text": match_text,
                        "match_type": "identical_question_text",
                        "reason": f"Question text already exists in database (matches ID: {match_id})."
                    }

    clean_indices = [idx for idx in range(len(records)) if idx not in duplicates_by_index]
    return {
        "duplicates_by_index": duplicates_by_index,
        "clean_indices": clean_indices
    }


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculates non-LLM text similarity using SequenceMatcher ratio."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    if norm1 == norm2:
        return 1.0
    if not norm1 or not norm2:
        return 0.0
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_probable_duplicates(
    conn: sqlite3.Connection,
    question_text: str,
    subject_id: Optional[int] = None,
    threshold: float = 0.82,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Scans a bounded subset of questions to flag probable duplicates.
    Protected by limit parameter to prevent runaway full-table scans.
    """
    query = "SELECT id, question_text FROM questions"
    params: List[Any] = []
    if subject_id:
        query += " WHERE subject_id = ?"
        params.append(subject_id)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

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
