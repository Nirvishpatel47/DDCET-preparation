from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
import sqlite3
from database.db import get_db

MISTAKE_LABELS = {
    "concept": "Didn't understand concept",
    "formula": "Forgot formula",
    "calculation": "Calculation error",
    "misread": "Misread question",
    "guess": "Guessed correctly",
    "time": "Ran out of time",
    "other": "Other reason"
}


def update_spaced_repetition(
    conn: sqlite3.Connection,
    question_id: str,
    is_correct: bool,
    confidence: Optional[str] = "medium",
    mistake_category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates the spaced repetition interval and next due date for a question
    following an attempt.
    """
    now = datetime.utcnow()
    now_iso = now.isoformat()
    today_date = now.date()

    row = conn.execute(
        """
        SELECT rs.*, q.difficulty 
        FROM revision_schedules rs
        JOIN questions q ON rs.question_id = q.id
        WHERE rs.question_id = ?
        """,
        (question_id,)
    ).fetchone()

    if not row:
        # First time answering this question
        diff_row = conn.execute("SELECT difficulty FROM questions WHERE id = ?", (question_id,)).fetchone()
        difficulty = diff_row["difficulty"] if diff_row else "medium"
        consecutive_correct = 1 if is_correct else 0
        consecutive_incorrect = 0 if is_correct else 1
        total_attempts = 1

        if not is_correct:
            interval_days = 1
        else:
            if confidence == "low":
                interval_days = 2
            elif confidence == "high":
                interval_days = 7
            else: # medium or default
                interval_days = 4

        next_due = today_date + timedelta(days=interval_days)

        conn.execute(
            """
            INSERT INTO revision_schedules (
                question_id, last_attempt_at, next_due_date, current_interval_days,
                consecutive_correct, consecutive_incorrect, total_attempts,
                difficulty_rating, last_confidence, last_mistake_category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id, now_iso, next_due.isoformat(), interval_days,
                consecutive_correct, consecutive_incorrect, total_attempts,
                difficulty, confidence, mistake_category
            )
        )
    else:
        # Existing schedule update
        prev_interval = row["current_interval_days"]
        prev_cons_correct = row["consecutive_correct"]
        prev_cons_incorrect = row["consecutive_incorrect"]
        total_attempts = row["total_attempts"] + 1

        if not is_correct:
            # Mistake during revision: shorten interval to 1 day immediately
            consecutive_correct = 0
            consecutive_incorrect = prev_cons_incorrect + 1
            interval_days = 1
        else:
            consecutive_incorrect = 0
            consecutive_correct = prev_cons_correct + 1

            # Multiplier progression based on streak and confidence
            if confidence == "low":
                mult = 1.2
            elif confidence == "high":
                mult = 2.0
            else:
                mult = 1.6

            # Extend interval gradually (capped at 90 days to ensure never permanently retired)
            interval_days = min(90, max(2, int(round(prev_interval * mult))))

        next_due = today_date + timedelta(days=interval_days)

        conn.execute(
            """
            UPDATE revision_schedules SET
                last_attempt_at = ?,
                next_due_date = ?,
                current_interval_days = ?,
                consecutive_correct = ?,
                consecutive_incorrect = ?,
                total_attempts = ?,
                last_confidence = ?,
                last_mistake_category = ?
            WHERE question_id = ?
            """,
            (
                now_iso, next_due.isoformat(), interval_days,
                consecutive_correct, consecutive_incorrect, total_attempts,
                confidence, mistake_category, question_id
            )
        )

    return {
        "question_id": question_id,
        "is_correct": is_correct,
        "next_due_date": next_due.isoformat(),
        "interval_days": interval_days,
        "confidence": confidence,
        "mistake_category": mistake_category
    }


def get_due_revisions(
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Fetches questions that are due or overdue for spaced revision today."""
    today_str = date.today().isoformat()
    with get_db() as conn:
        query = """
            SELECT 
                q.id, q.question_text, q.difficulty, q.explanation,
                s.name as subject, t.name as topic, st.name as subtopic,
                rs.next_due_date, rs.current_interval_days, rs.consecutive_correct,
                rs.consecutive_incorrect, rs.total_attempts, rs.last_confidence,
                rs.last_mistake_category
            FROM revision_schedules rs
            JOIN questions q ON rs.question_id = q.id
            JOIN subjects s ON q.subject_id = s.id
            JOIN topics t ON q.topic_id = t.id
            JOIN subtopics st ON q.subtopic_id = st.id
            WHERE rs.next_due_date <= ? AND q.verified = 1
        """
        params = [today_str]
        if subject_id:
            query += " AND q.subject_id = ?"
            params.append(subject_id)
        if topic_id:
            query += " AND q.topic_id = ?"
            params.append(topic_id)

        query += " ORDER BY rs.next_due_date ASC, rs.consecutive_incorrect DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "question": r["question_text"],
            "difficulty": r["difficulty"],
            "explanation": r["explanation"],
            "subject": r["subject"],
            "topic": r["topic"],
            "subtopic": r["subtopic"],
            "next_due_date": r["next_due_date"],
            "interval_days": r["current_interval_days"],
            "consecutive_correct": r["consecutive_correct"],
            "consecutive_incorrect": r["consecutive_incorrect"],
            "total_attempts": r["total_attempts"],
            "last_confidence": r["last_confidence"],
            "last_mistake_category": r["last_mistake_category"],
            "mistake_label": MISTAKE_LABELS.get(r["last_mistake_category"], "N/A")
        })
    return results


def get_mistake_patterns() -> List[Dict[str, Any]]:
    """Analyzes mistake logs to display recurring error patterns to the student."""
    with get_db() as conn:
        query = """
            SELECT 
                a.mistake_category,
                COUNT(*) as count,
                COUNT(DISTINCT a.question_id) as unique_questions,
                t.name as top_topic
            FROM attempts a
            JOIN questions q ON a.question_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE a.mistake_category IS NOT NULL AND a.is_correct = 0
            GROUP BY a.mistake_category
            ORDER BY count DESC
        """
        rows = conn.execute(query).fetchall()

    total_mistakes = sum(r["count"] for r in rows) if rows else 0
    patterns = []
    for r in rows:
        pct = (r["count"] / total_mistakes * 100) if total_mistakes > 0 else 0
        patterns.append({
            "category": r["mistake_category"],
            "label": MISTAKE_LABELS.get(r["mistake_category"], r["mistake_category"].capitalize()),
            "count": r["count"],
            "percentage": round(pct, 1),
            "unique_questions": r["unique_questions"],
            "example_topic": r["top_topic"]
        })
    return patterns
