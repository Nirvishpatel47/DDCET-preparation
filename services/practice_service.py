import uuid
import json
import random
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import sqlite3
from database.db import get_db, get_all_settings
from services.adaptive_service import calculate_adaptive_priorities
from services.revision_service import update_spaced_repetition


def create_practice_session(
    session_type: str = "daily_mixed",
    size: int = 20,
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    subtopic_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    time_limit_minutes: Optional[int] = None
) -> Dict[str, Any]:
    """
    Creates a new study/practice/mock session with intelligent question selection.
    Guarantees no duplicate questions within the session.
    """
    settings = get_all_settings()
    session_id = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat()
    today_str = date.today().isoformat()

    # Determine time limit
    if session_type == "full_mock":
        duration_mins = int(settings.get("mock_exam_duration_mins", 90))
        time_limit_seconds = duration_mins * 60
        target_size = int(settings.get("mock_exam_total_questions", 100))
    elif session_type == "timed" or time_limit_minutes:
        time_limit_seconds = (time_limit_minutes or 20) * 60
        target_size = size
    else:
        time_limit_seconds = 0
        target_size = size

    selected_questions: List[Dict[str, Any]] = []

    with get_db() as conn:
        # Check verified question pool availability
        count_row = conn.execute("SELECT COUNT(*) as cnt FROM questions WHERE verified = 1").fetchone()
        total_verified_available = count_row["cnt"] if count_row else 0
        
        if total_verified_available == 0:
            # Fallback to unverified if no verified exists yet, but flag clearly
            pass

        selected_question_ids: List[str] = []

        if session_type == "incorrect_only":
            # Select exclusively from previously attempted questions that were incorrect
            diff_clause = "AND q.difficulty = ?" if difficulty else ""
            params = [difficulty, target_size] if difficulty else [target_size]
            inc_rows = conn.execute(
                f"""
                SELECT DISTINCT a.question_id
                FROM attempts a
                JOIN questions q ON a.question_id = q.id
                WHERE a.is_correct = 0 AND q.verified = 1 {diff_clause}
                ORDER BY a.attempted_at DESC
                LIMIT ?
                """,
                params
            ).fetchall()
            for r in inc_rows:
                selected_question_ids.append(r["question_id"])

        elif session_type == "revision_only":
            # Priority: questions with next_due_date <= today, or previously incorrect questions
            diff_clause = "AND q.difficulty = ?" if difficulty else ""
            rev_params = [today_str, difficulty, target_size] if difficulty else [today_str, target_size]
            rev_rows = conn.execute(
                f"""
                SELECT q.id
                FROM revision_schedules rs
                JOIN questions q ON rs.question_id = q.id
                WHERE rs.next_due_date <= ? AND q.verified = 1 {diff_clause}
                ORDER BY rs.consecutive_incorrect DESC, rs.next_due_date ASC
                LIMIT ?
                """,
                rev_params
            ).fetchall()
            for r in rev_rows:
                selected_question_ids.append(r["id"])

            # If not enough overdue, fill with previously attempted questions that were incorrect
            if len(selected_question_ids) < target_size:
                needed = target_size - len(selected_question_ids)
                fill_params = [*selected_question_ids, difficulty, needed] if difficulty else [*selected_question_ids, needed]
                diff_filter = "AND q.difficulty = ?" if difficulty else ""
                fill_rows = conn.execute(
                    """
                    SELECT DISTINCT a.question_id
                    FROM attempts a
                    JOIN questions q ON a.question_id = q.id
                    WHERE a.is_correct = 0 AND q.verified = 1 {}
                    AND a.question_id NOT IN ({})
                    ORDER BY a.attempted_at DESC
                    LIMIT ?
                    """.format(
                        diff_filter,
                        ",".join(["?"] * len(selected_question_ids)) if selected_question_ids else "''"
                    ),
                    fill_params if selected_question_ids else ([difficulty, needed] if difficulty else [needed])
                ).fetchall()
                for r in fill_rows:
                    selected_question_ids.append(r["question_id"])

        elif session_type == "weak_topic":
            # Pull priority list and pick questions from top weakest topics
            priorities = calculate_adaptive_priorities()
            weakest_topics = [p for p in priorities if p["components"]["weakness_score"] > 0.4 or p["is_diagnostic"]]
            if not weakest_topics and priorities:
                weakest_topics = priorities[:3]
            
            diff_clause = "AND q.difficulty = ?" if difficulty else ""
            for p in weakest_topics:
                if len(selected_question_ids) >= target_size:
                    break
                needed = target_size - len(selected_question_ids)
                per_topic_cap = max(3, target_size // max(1, len(weakest_topics)))
                take = min(needed, per_topic_cap)

                q_params = [*selected_question_ids, p["topic_id"]] if selected_question_ids else [p["topic_id"]]
                if difficulty:
                    q_params.append(difficulty)
                q_params.append(take)

                rows = conn.execute(
                    """
                    SELECT q.id FROM questions q
                    WHERE q.topic_id = ? AND q.verified = 1 {}
                    AND q.id NOT IN ({})
                    ORDER BY RANDOM()
                    LIMIT ?
                    """.format(
                        diff_clause,
                        ",".join(["?"] * len(selected_question_ids)) if selected_question_ids else "''"
                    ),
                    [p["topic_id"], *([difficulty] if difficulty else []), *([*selected_question_ids] if selected_question_ids else []), take] if not selected_question_ids else [*selected_question_ids, p["topic_id"], *([difficulty] if difficulty else []), take]
                ).fetchall()
                for r in rows:
                    selected_question_ids.append(r["id"])

        elif session_type in ["subject", "topic", "subtopic"]:
            # Targeted filter
            where_clauses = ["q.verified = 1"]
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
                params.append(difficulty)

            where_str = " AND ".join(where_clauses)
            rows = conn.execute(
                f"SELECT q.id FROM questions q WHERE {where_str} ORDER BY RANDOM() LIMIT ?",
                [*params, target_size]
            ).fetchall()
            for r in rows:
                selected_question_ids.append(r["id"])

        else:
            # Daily Mixed practice or Full Mock:
            # Step 1: Include due revision items first (up to 25% of session)
            rev_cap = max(2, int(target_size * 0.25))
            diff_clause = "AND q.difficulty = ?" if difficulty else ""
            rev_params = [today_str, difficulty, rev_cap] if difficulty else [today_str, rev_cap]
            rev_rows = conn.execute(
                f"""
                SELECT q.id
                FROM revision_schedules rs
                JOIN questions q ON rs.question_id = q.id
                WHERE rs.next_due_date <= ? AND q.verified = 1 {diff_clause}
                ORDER BY rs.next_due_date ASC
                LIMIT ?
                """,
                rev_params
            ).fetchall()
            for r in rev_rows:
                selected_question_ids.append(r["id"])

            # Step 2: Use adaptive priority topics to balance remaining slots
            priorities = calculate_adaptive_priorities()
            topic_max_cap_pct = float(settings.get("topic_max_cap_pct", 0.30))
            max_per_topic = max(2, int(target_size * topic_max_cap_pct))

            for p in priorities:
                if len(selected_question_ids) >= target_size:
                    break
                needed = target_size - len(selected_question_ids)
                quota = min(needed, max_per_topic)

                diff_cond = "AND q.difficulty = ?" if difficulty else ""
                diff_args = [difficulty] if difficulty else []

                # Prioritize unseen verified questions in this high-priority topic
                rows = conn.execute(
                    """
                    SELECT q.id FROM questions q
                    WHERE q.topic_id = ? AND q.verified = 1 {}
                    AND q.id NOT IN (SELECT question_id FROM attempts)
                    AND q.id NOT IN ({})
                    ORDER BY RANDOM()
                    LIMIT ?
                    """.format(diff_cond, ",".join(["?"] * len(selected_question_ids)) if selected_question_ids else "''"),
                    [p["topic_id"], *diff_args, *selected_question_ids, quota] if selected_question_ids else [p["topic_id"], *diff_args, quota]
                ).fetchall()
                for r in rows:
                    selected_question_ids.append(r["id"])

                # If not enough unseen in this topic, take general questions from this topic
                if len(selected_question_ids) < target_size and len(rows) < quota:
                    more_needed = quota - len(rows)
                    rows_more = conn.execute(
                        """
                        SELECT q.id FROM questions q
                        WHERE q.topic_id = ? AND q.verified = 1 {}
                        AND q.id NOT IN ({})
                        ORDER BY RANDOM()
                        LIMIT ?
                        """.format(diff_cond, ",".join(["?"] * len(selected_question_ids)) if selected_question_ids else "''"),
                        [p["topic_id"], *diff_args, *selected_question_ids, more_needed] if selected_question_ids else [p["topic_id"], *diff_args, more_needed]
                    ).fetchall()
                    for r in rows_more:
                        selected_question_ids.append(r["id"])

        # Fallback if target_size not met (e.g. small bank or unverified bank or specific difficulty)
        if len(selected_question_ids) < target_size:
            needed = target_size - len(selected_question_ids)
            not_in_clause = ",".join(["?"] * len(selected_question_ids)) if selected_question_ids else "''"
            diff_cond = "AND q.difficulty = ?" if difficulty else ""
            diff_args = [difficulty] if difficulty else []
            fallback_rows = conn.execute(
                f"""
                SELECT q.id FROM questions q
                WHERE q.id NOT IN ({not_in_clause}) {diff_cond}
                ORDER BY q.verified DESC, RANDOM()
                LIMIT ?
                """,
                [*selected_question_ids, *diff_args, needed] if selected_question_ids else [*diff_args, needed]
            ).fetchall()
            for r in fallback_rows:
                selected_question_ids.append(r["id"])

        # Final fallback without difficulty if still not enough
        if len(selected_question_ids) < target_size and difficulty:
            needed = target_size - len(selected_question_ids)
            not_in_clause = ",".join(["?"] * len(selected_question_ids)) if selected_question_ids else "''"
            fallback_rows = conn.execute(
                f"""
                SELECT q.id FROM questions q
                WHERE q.id NOT IN ({not_in_clause})
                ORDER BY q.verified DESC, RANDOM()
                LIMIT ?
                """,
                [*selected_question_ids, needed] if selected_question_ids else [needed]
            ).fetchall()
            for r in fallback_rows:
                selected_question_ids.append(r["id"])

        actual_total = len(selected_question_ids)
        if actual_total == 0:
            raise ValueError("No questions available in the question bank matching the session criteria.")

        # Create session record
        conn.execute(
            """
            INSERT INTO sessions (
                id, session_type, target_subject_id, target_topic_id, target_subtopic_id,
                total_questions, answered_questions, time_limit_seconds, started_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                session_id, session_type, subject_id, topic_id, subtopic_id,
                actual_total, time_limit_seconds, now_iso
            )
        )

        # Fetch question option details to perform option randomization
        q_map = {}
        if selected_question_ids:
            placeholders = ",".join(["?"] * len(selected_question_ids))
            q_data = conn.execute(
                f"SELECT id, option_a, option_b, option_c, option_d, correct_answer FROM questions WHERE id IN ({placeholders})",
                selected_question_ids
            ).fetchall()
            for row in q_data:
                q_map[row["id"]] = row

        # Insert session questions in order with randomized option presentation
        letters = ["A", "B", "C", "D"]
        for idx, qid in enumerate(selected_question_ids):
            q_info = q_map.get(qid)
            shuffled_opts_json = None
            shuffled_correct = None
            if q_info:
                orig_opts = {
                    "A": q_info["option_a"],
                    "B": q_info["option_b"],
                    "C": q_info["option_c"],
                    "D": q_info["option_d"]
                }
                orig_ans = q_info["correct_answer"]
                corr_val = orig_opts.get(orig_ans)

                # Randomly permute the 4 option texts
                opt_texts = list(orig_opts.values())
                random.shuffle(opt_texts)

                shuffled_opts = {letters[i]: opt_texts[i] for i in range(4)}
                for let, val in shuffled_opts.items():
                    if val == corr_val:
                        shuffled_correct = let
                        break
                shuffled_opts_json = json.dumps(shuffled_opts)

            conn.execute(
                """
                INSERT INTO session_questions (
                    session_id, question_id, order_index, is_marked_for_review, is_answered,
                    shuffled_options, shuffled_correct
                ) VALUES (?, ?, ?, 0, 0, ?, ?)
                """,
                (session_id, qid, idx + 1, shuffled_opts_json, shuffled_correct)
            )

    return get_session_state(session_id)


def get_session_state(session_id: str) -> Dict[str, Any]:
    """Fetches the complete session state, questions, answers, and time left."""
    with get_db() as conn:
        session_row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session_row:
            raise ValueError(f"Session '{session_id}' not found.")

        is_mock = session_row["session_type"] == "full_mock"
        is_completed = bool(session_row["is_completed"])

        # Fetch questions for this session
        q_rows = conn.execute(
            """
            SELECT 
                sq.order_index, sq.selected_option, sq.is_marked_for_review,
                sq.is_answered, sq.is_correct, sq.time_spent_seconds,
                sq.confidence, sq.mistake_category,
                sq.shuffled_options, sq.shuffled_correct,
                q.id as question_id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
                q.correct_answer, q.explanation, q.difficulty, q.verified,
                s.name as subject_name, t.name as topic_name, st.name as subtopic_name
            FROM session_questions sq
            JOIN questions q ON sq.question_id = q.id
            JOIN subjects s ON q.subject_id = s.id
            JOIN topics t ON q.topic_id = t.id
            JOIN subtopics st ON q.subtopic_id = st.id
            WHERE sq.session_id = ?
            ORDER BY sq.order_index ASC
            """,
            (session_id,)
        ).fetchall()

    questions = []
    for r in q_rows:
        # In full mock exams, NEVER reveal correct_answer or explanation until completed!
        hide_answers = is_mock and not is_completed
        if r["shuffled_options"] and r["shuffled_correct"]:
            opts = json.loads(r["shuffled_options"])
            ans = r["shuffled_correct"]
        else:
            opts = {
                "A": r["option_a"],
                "B": r["option_b"],
                "C": r["option_c"],
                "D": r["option_d"]
            }
            ans = r["correct_answer"]

        questions.append({
            "order_index": r["order_index"],
            "question_id": r["question_id"],
            "question": r["question_text"],
            "options": opts,
            "correct_answer": None if hide_answers else ans,
            "explanation": None if hide_answers else r["explanation"],
            "difficulty": r["difficulty"],
            "verified": bool(r["verified"]),
            "subject": r["subject_name"],
            "topic": r["topic_name"],
            "subtopic": r["subtopic_name"],
            "selected_option": r["selected_option"],
            "is_marked_for_review": bool(r["is_marked_for_review"]),
            "is_answered": bool(r["is_answered"]),
            "is_correct": None if hide_answers else (bool(r["is_correct"]) if r["is_correct"] is not None else None),
            "time_spent_seconds": r["time_spent_seconds"],
            "confidence": r["confidence"],
            "mistake_category": r["mistake_category"]
        })

    return {
        "session_id": session_row["id"],
        "session_type": session_row["session_type"],
        "total_questions": session_row["total_questions"],
        "answered_questions": session_row["answered_questions"],
        "correct_count": session_row["correct_count"],
        "incorrect_count": session_row["incorrect_count"],
        "unanswered_count": session_row["unanswered_count"],
        "total_score": session_row["total_score"],
        "accuracy_pct": session_row["accuracy_pct"],
        "time_taken_seconds": session_row["time_taken_seconds"],
        "time_limit_seconds": session_row["time_limit_seconds"],
        "is_completed": bool(session_row["is_completed"]),
        "started_at": session_row["started_at"],
        "completed_at": session_row["completed_at"],
        "questions": questions
    }


def record_question_answer(
    session_id: str,
    question_id: str,
    selected_option: Optional[str] = None,
    time_spent_seconds: int = 0,
    is_marked_for_review: bool = False,
    confidence: Optional[str] = None,
    mistake_category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Auto-saves a question's response in the active session.
    Calculates correctness and updates spaced repetition schedule.
    """
    with get_db() as conn:
        sq_row = conn.execute(
            """
            SELECT sq.shuffled_correct, q.correct_answer
            FROM session_questions sq
            JOIN questions q ON sq.question_id = q.id
            WHERE sq.session_id = ? AND sq.question_id = ?
            """,
            (session_id, question_id)
        ).fetchone()

        if not sq_row:
            raise ValueError(f"Question '{question_id}' in session '{session_id}' not found.")
        
        correct_ans = sq_row["shuffled_correct"] or sq_row["correct_answer"]
        is_answered = 1 if selected_option is not None and selected_option in ["A", "B", "C", "D"] else 0
        is_correct = 1 if (is_answered and selected_option == correct_ans) else (0 if is_answered else None)

        conn.execute(
            """
            UPDATE session_questions SET
                selected_option = ?,
                is_answered = ?,
                is_correct = ?,
                time_spent_seconds = time_spent_seconds + ?,
                is_marked_for_review = ?,
                confidence = ?,
                mistake_category = ?
            WHERE session_id = ? AND question_id = ?
            """,
            (
                selected_option,
                is_answered,
                is_correct,
                max(0, time_spent_seconds),
                1 if is_marked_for_review else 0,
                confidence,
                mistake_category,
                session_id,
                question_id
            )
        )

        # Update session answered count
        ans_count_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM session_questions WHERE session_id = ? AND is_answered = 1",
            (session_id,)
        ).fetchone()
        conn.execute(
            "UPDATE sessions SET answered_questions = ? WHERE id = ?",
            (ans_count_row["cnt"], session_id)
        )

    return {
        "status": "saved",
        "question_id": question_id,
        "selected_option": selected_option,
        "is_answered": bool(is_answered),
        "is_correct": bool(is_correct) if is_correct is not None else None,
        "correct_answer": correct_ans
    }


def complete_session(session_id: str, time_taken_seconds: int) -> Dict[str, Any]:
    """
    Submits and finalizes a session:
    - Calculates marks using the configured DDCET marking scheme
    - Computes accuracy percentage and category breakdowns
    - Persists individual attempts in the attempts log for analytics
    - Updates spaced repetition schedules
    """
    settings = get_all_settings()
    mark_correct = float(settings.get("marking_correct", 1.0))
    mark_incorrect = float(settings.get("marking_incorrect", -0.25))
    mark_unanswered = float(settings.get("marking_unanswered", 0.0))

    now_iso = datetime.utcnow().isoformat()

    with get_db() as conn:
        session_row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session_row:
            raise ValueError(f"Session '{session_id}' not found.")

        # Get all session questions
        sq_rows = conn.execute(
            """
            SELECT sq.*, q.correct_answer as orig_correct_answer, q.difficulty, q.subject_id, q.topic_id
            FROM session_questions sq
            JOIN questions q ON sq.question_id = q.id
            WHERE sq.session_id = ?
            ORDER BY sq.order_index ASC
            """,
            (session_id,)
        ).fetchall()

        correct_cnt = 0
        incorrect_cnt = 0
        unanswered_cnt = 0
        total_score = 0.0

        for r in sq_rows:
            sel = r["selected_option"]
            ans = r["shuffled_correct"] or r["orig_correct_answer"]
            time_spent = r["time_spent_seconds"] or 0
            conf = r["confidence"]
            mistake = r["mistake_category"]

            if sel and sel in ["A", "B", "C", "D"]:
                if sel == ans:
                    correct_cnt += 1
                    total_score += mark_correct
                    is_corr = 1
                else:
                    incorrect_cnt += 1
                    total_score += mark_incorrect
                    is_corr = 0

                # Log into attempts table
                conn.execute(
                    """
                    INSERT INTO attempts (
                        question_id, session_id, selected_option, is_correct,
                        time_spent_seconds, confidence, mistake_category, attempted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (r["question_id"], session_id, sel, is_corr, time_spent, conf, mistake, now_iso)
                )

                # Update spaced repetition schedule
                update_spaced_repetition(
                    conn,
                    question_id=r["question_id"],
                    is_correct=(is_corr == 1),
                    confidence=conf,
                    mistake_category=mistake
                )
            else:
                unanswered_cnt += 1
                total_score += mark_unanswered

        total_q = len(sq_rows)
        accuracy_pct = (correct_cnt / max(1, correct_cnt + incorrect_cnt)) * 100 if (correct_cnt + incorrect_cnt) > 0 else 0.0

        conn.execute(
            """
            UPDATE sessions SET
                is_completed = 1,
                completed_at = ?,
                time_taken_seconds = ?,
                correct_count = ?,
                incorrect_count = ?,
                unanswered_count = ?,
                total_score = ?,
                accuracy_pct = ?
            WHERE id = ?
            """,
            (
                now_iso,
                time_taken_seconds,
                correct_cnt,
                incorrect_cnt,
                unanswered_cnt,
                round(total_score, 2),
                round(accuracy_pct, 1),
                session_id
            )
        )

    return get_session_summary(session_id)


def get_session_summary(session_id: str) -> Dict[str, Any]:
    """Provides a detailed diagnostic report of a completed session."""
    with get_db() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        # Breakdown by subject
        subject_stats = conn.execute(
            """
            SELECT 
                s.name as subject,
                COUNT(*) as total,
                SUM(CASE WHEN sq.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                SUM(CASE WHEN sq.is_correct = 0 THEN 1 ELSE 0 END) as incorrect,
                SUM(CASE WHEN sq.is_answered = 0 THEN 1 ELSE 0 END) as unanswered
            FROM session_questions sq
            JOIN questions q ON sq.question_id = q.id
            JOIN subjects s ON q.subject_id = s.id
            WHERE sq.session_id = ?
            GROUP BY s.name
            """,
            (session_id,)
        ).fetchall()

        # Breakdown by difficulty
        diff_stats = conn.execute(
            """
            SELECT 
                q.difficulty,
                COUNT(*) as total,
                SUM(CASE WHEN sq.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                SUM(CASE WHEN sq.is_correct = 0 THEN 1 ELSE 0 END) as incorrect
            FROM session_questions sq
            JOIN questions q ON sq.question_id = q.id
            WHERE sq.session_id = ?
            GROUP BY q.difficulty
            """,
            (session_id,)
        ).fetchall()

        # Mistake breakdown
        mistake_stats = conn.execute(
            """
            SELECT 
                sq.mistake_category,
                COUNT(*) as count
            FROM session_questions sq
            WHERE sq.session_id = ? AND sq.mistake_category IS NOT NULL
            GROUP BY sq.mistake_category
            """,
            (session_id,)
        ).fetchall()

    return {
        "session_id": session["id"],
        "session_type": session["session_type"],
        "total_questions": session["total_questions"],
        "correct_count": session["correct_count"],
        "incorrect_count": session["incorrect_count"],
        "unanswered_count": session["unanswered_count"],
        "total_score": session["total_score"],
        "accuracy_pct": session["accuracy_pct"],
        "time_taken_seconds": session["time_taken_seconds"],
        "average_time_per_question": round(session["time_taken_seconds"] / max(1, session["total_questions"]), 1),
        "is_completed": bool(session["is_completed"]),
        "completed_at": session["completed_at"],
        "subject_breakdown": [dict(r) for r in subject_stats],
        "difficulty_breakdown": [dict(r) for r in diff_stats],
        "mistake_breakdown": [dict(r) for r in mistake_stats]
    }
