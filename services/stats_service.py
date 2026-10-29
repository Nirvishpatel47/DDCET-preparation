import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

from database.db import get_db
from services.auth_service import get_current_user


def compute_comprehensive_stats() -> Dict[str, Any]:
    """
    Computes complete student performance metrics, including granular
    Topic-Wise MCQs done or not, accuracy, mastery levels, and battle metrics.
    """
    user = get_current_user()
    email = user.get("email", "cadet@ddcet.local")
    display_name = user.get("display_name", "DDCET Cadet")
    avatar = user.get("avatar", "⚡")

    with get_db() as conn:
        # 1. Overall attempt summary
        overall_row = conn.execute(
            """
            SELECT 
                COUNT(*) as total_attempts,
                COUNT(DISTINCT question_id) as unique_attempted,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as total_correct,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as total_incorrect,
                AVG(time_spent_seconds) as avg_speed,
                SUM(time_spent_seconds) as total_time_sec
            FROM attempts
            """
        ).fetchone()

        total_attempts = overall_row["total_attempts"] or 0
        unique_attempted = overall_row["unique_attempted"] or 0
        total_correct = overall_row["total_correct"] or 0
        total_incorrect = overall_row["total_incorrect"] or 0
        avg_speed = round(overall_row["avg_speed"] or 0.0, 1)
        total_time_min = round((overall_row["total_time_sec"] or 0) / 60.0, 1)

        accuracy_pct = round((total_correct / total_attempts * 100), 2) if total_attempts > 0 else 0.0
        # DDCET Marking Scheme: +1 for correct, -0.25 for incorrect
        total_score = round((total_correct * 1.0) - (total_incorrect * 0.25), 2)

        # 2. Daily Streak Calculation
        dates_rows = conn.execute(
            "SELECT DISTINCT date(attempted_at) as attempt_date FROM attempts ORDER BY attempt_date DESC"
        ).fetchall()
        
        attempt_dates = [r["attempt_date"] for r in dates_rows]
        streak_days = 0
        if attempt_dates:
            today = date.today()
            yesterday = today - timedelta(days=1)
            first_date = date.fromisoformat(attempt_dates[0])
            
            # Check if active today or yesterday
            if first_date in (today, yesterday):
                streak_days = 1
                curr = first_date
                for next_str in attempt_dates[1:]:
                    d = date.fromisoformat(next_str)
                    if curr - d == timedelta(days=1):
                        streak_days += 1
                        curr = d
                    else:
                        break

        # 3. Topic-Wise Detailed Breakdown (MCQs done or not, accuracy, mastery)
        topic_summary_rows = conn.execute(
            """
            SELECT 
                s.id as subject_id,
                s.name as subject_name,
                t.id as topic_id,
                t.name as topic_name,
                COUNT(q.id) as total_in_bank,
                COUNT(DISTINCT a.question_id) as questions_attempted,
                SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as topic_correct,
                SUM(CASE WHEN a.is_correct = 0 THEN 1 ELSE 0 END) as topic_incorrect,
                AVG(a.time_spent_seconds) as topic_avg_speed
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            LEFT JOIN questions q ON q.topic_id = t.id AND q.verified = 1
            LEFT JOIN attempts a ON a.question_id = q.id
            GROUP BY s.id, t.id
            ORDER BY s.name, t.name
            """
        ).fetchall()

        topic_stats: Dict[str, Any] = {}
        topics_mastered = 0
        topics_done_count = 0
        topics_in_progress_count = 0
        topics_not_started_count = 0
        total_topics = len(topic_summary_rows)

        for r in topic_summary_rows:
            t_key = f"{r['subject_name']}::{r['topic_name']}"
            t_bank = r["total_in_bank"] or 0
            t_att = r["questions_attempted"] or 0
            t_corr = r["topic_correct"] or 0
            t_inc = r["topic_incorrect"] or 0
            t_tot = t_corr + t_inc
            t_acc = round((t_corr / t_tot * 100), 1) if t_tot > 0 else 0.0

            # Determine Done or Not Done status
            if t_bank > 0 and t_att >= t_bank:
                status = "DONE"
                status_label = "Completed"
                topics_done_count += 1
            elif t_att > 0:
                status = "IN_PROGRESS"
                status_label = "In Progress"
                topics_in_progress_count += 1
            else:
                status = "NOT_STARTED"
                status_label = "Not Started"
                topics_not_started_count += 1

            # Determine Mastery Level
            if t_acc >= 85.0 and t_att >= 4:
                mastery = "Mastered"
                mastery_icon = "🏆"
                topics_mastered += 1
            elif t_acc >= 70.0 and t_att >= 3:
                mastery = "Proficient"
                mastery_icon = "⚡"
            elif t_att >= 3:
                mastery = "Needs Practice"
                mastery_icon = "⚠️"
            else:
                mastery = "Untested"
                mastery_icon = "⚪"

            completion_pct = round((t_att / t_bank * 100), 1) if t_bank > 0 else 0.0

            topic_stats[t_key] = {
                "subject": r["subject_name"],
                "topic": r["topic_name"],
                "total_in_bank": t_bank,
                "attempted": t_att,
                "remaining": max(0, t_bank - t_att),
                "correct": t_corr,
                "incorrect": t_inc,
                "accuracy_pct": t_acc,
                "completion_pct": completion_pct,
                "status": status,
                "status_label": status_label,
                "done_ratio": f"{t_att}/{t_bank}",
                "is_done": status == "DONE",
                "mastery": mastery,
                "mastery_icon": mastery_icon,
                "avg_speed": round(r["topic_avg_speed"] or 0.0, 1)
            }

        # 4. Mock Exams Summary
        mock_rows = conn.execute(
            """
            SELECT id, total_score, accuracy_pct, total_questions, correct_count,
                   incorrect_count, unanswered_count, time_taken_seconds, completed_at
            FROM sessions
            WHERE session_type = 'full_mock' AND is_completed = 1
            ORDER BY completed_at DESC
            LIMIT 5
            """
        ).fetchall()

        mock_stats = [
            {
                "id": m["id"],
                "score": m["total_score"],
                "accuracy": m["accuracy_pct"],
                "correct": m["correct_count"],
                "incorrect": m["incorrect_count"],
                "unanswered": m["unanswered_count"],
                "completed_at": m["completed_at"]
            }
            for m in mock_rows
        ]

    now_iso = datetime.utcnow().isoformat()

    return {
        "email": email,
        "display_name": display_name,
        "avatar": avatar,
        "total_questions": total_attempts,
        "unique_questions_answered": unique_attempted,
        "correct_count": total_correct,
        "incorrect_count": total_incorrect,
        "accuracy_pct": accuracy_pct,
        "total_score": total_score,
        "study_time_minutes": total_time_min,
        "streak_days": streak_days,
        "avg_speed_seconds": avg_speed,
        "topics_mastered": topics_mastered,
        "topics_done_count": topics_done_count,
        "topics_in_progress_count": topics_in_progress_count,
        "topics_not_started_count": topics_not_started_count,
        "topics_total": total_topics,
        "topic_stats": topic_stats,
        "mock_stats": mock_stats,
        "last_active": now_iso,
        "updated_at": now_iso
    }
