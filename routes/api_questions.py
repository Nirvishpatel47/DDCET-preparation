from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from database.db import get_db

router = APIRouter(prefix="/api/questions", tags=["Questions"])


@router.get("/hierarchy")
def get_hierarchy():
    """Returns the full hierarchical tree: Subjects -> Topics -> Subtopics."""
    with get_db() as conn:
        subjects_rows = conn.execute("SELECT id, name, syllabus_weight FROM subjects ORDER BY name").fetchall()
        topics_rows = conn.execute("SELECT id, subject_id, name, syllabus_weight FROM topics ORDER BY name").fetchall()
        subtopics_rows = conn.execute("SELECT id, topic_id, name FROM subtopics ORDER BY name").fetchall()

        subtopics_by_topic: Dict[int, List[Dict[str, Any]]] = {}
        for st in subtopics_rows:
            subtopics_by_topic.setdefault(st["topic_id"], []).append({
                "id": st["id"],
                "name": st["name"]
            })

        topics_by_subject: Dict[int, List[Dict[str, Any]]] = {}
        for t in topics_rows:
            topics_by_subject.setdefault(t["subject_id"], []).append({
                "id": t["id"],
                "name": t["name"],
                "syllabus_weight": t["syllabus_weight"],
                "subtopics": subtopics_by_topic.get(t["id"], [])
            })

        tree = []
        for s in subjects_rows:
            tree.append({
                "id": s["id"],
                "name": s["name"],
                "syllabus_weight": s["syllabus_weight"],
                "topics": topics_by_subject.get(s["id"], [])
            })

    return {"hierarchy": tree}


@router.get("")
def list_questions(
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    subtopic_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    verified_only: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Paginated question bank browser.
    Prevents loading entire question bank into browser memory.
    """
    offset = (page - 1) * limit
    where_clauses = ["1=1"]
    params = []

    if subject_id:
        where_clauses.append("q.subject_id = ?")
        params.append(subject_id)
    if topic_id:
        where_clauses.append("q.topic_id = ?")
        params.append(topic_id)
    if subtopic_id:
        where_clauses.append("q.subtopic_id = ?")
        params.append(subtopic_id)
    if difficulty:
        where_clauses.append("q.difficulty = ?")
        params.append(difficulty.lower())
    if verified_only is not None:
        where_clauses.append("q.verified = ?")
        params.append(1 if verified_only else 0)
    if search:
        where_clauses.append("(q.question_text LIKE ? OR q.id LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_str = " AND ".join(where_clauses)

    with get_db() as conn:
        count_row = conn.execute(
            f"SELECT COUNT(*) as total FROM questions q WHERE {where_str}",
            params
        ).fetchone()
        total_records = count_row["total"] if count_row else 0

        query = f"""
            SELECT q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
                   q.correct_answer, q.explanation, q.difficulty, q.verified, q.created_at,
                   s.name as subject, t.name as topic, st.name as subtopic
            FROM questions q
            JOIN subjects s ON q.subject_id = s.id
            JOIN topics t ON q.topic_id = t.id
            JOIN subtopics st ON q.subtopic_id = st.id
            WHERE {where_str}
            ORDER BY q.created_at DESC, q.id ASC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query, [*params, limit, offset]).fetchall()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "question": r["question_text"],
            "options": {
                "A": r["option_a"],
                "B": r["option_b"],
                "C": r["option_c"],
                "D": r["option_d"]
            },
            "correct_answer": r["correct_answer"],
            "explanation": r["explanation"],
            "difficulty": r["difficulty"],
            "verified": bool(r["verified"]),
            "subject": r["subject"],
            "topic": r["topic"],
            "subtopic": r["subtopic"],
            "created_at": r["created_at"]
        })

    return {
        "page": page,
        "limit": limit,
        "total": total_records,
        "pages": (total_records + limit - 1) // limit if total_records > 0 else 1,
        "questions": items
    }
