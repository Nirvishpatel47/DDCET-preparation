from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import sqlite3
from database.db import get_db
from services.adaptive_service import calculate_adaptive_priorities
from services.revision_service import get_due_revisions, get_mistake_patterns


def get_dashboard_analytics() -> Dict[str, Any]:
    """
    Computes all analytical metrics for the primary dashboard, answering:
    'What should I do during my next 60 minutes?'
    """
    today_str = date.today().isoformat()
    now = datetime.utcnow()
    seven_days_ago = (now - timedelta(days=7)).isoformat()
    fourteen_days_ago = (now - timedelta(days=14)).isoformat()

    with get_db() as conn:
        # 1. Questions answered today & daily time spent
        today_row = conn.execute(
            """
            SELECT 
                COUNT(*) as answered_today,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_today,
                SUM(time_spent_seconds) as time_spent_today
            FROM attempts
            WHERE date(attempted_at) = ?
            """,
            (today_str,)
        ).fetchone()

        answered_today = today_row["answered_today"] or 0
        correct_today = today_row["correct_today"] or 0
        time_today_sec = today_row["time_spent_today"] or 0
        accuracy_today = (correct_today / answered_today * 100) if answered_today > 0 else 0.0

        # 2. Overall lifetime accuracy & stats
        all_row = conn.execute(
            """
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as total_correct,
                AVG(time_spent_seconds) as avg_solving_speed
            FROM attempts
            """
        ).fetchone()

        total_attempts = all_row["total_attempts"] or 0
        total_correct = all_row["total_correct"] or 0
        overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
        avg_solving_speed = round(all_row["avg_solving_speed"] or 0.0, 1)

        # 3. 7-Day Accuracy Trend (by day)
        trend_rows = conn.execute(
            """
            SELECT 
                date(attempted_at) as day,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM attempts
            WHERE attempted_at >= ?
            GROUP BY date(attempted_at)
            ORDER BY day ASC
            """,
            (seven_days_ago,)
        ).fetchall()

        daily_trend = []
        for r in trend_rows:
            tot = r["total"]
            corr = r["correct"]
            daily_trend.append({
                "date": r["day"],
                "total": tot,
                "accuracy": round((corr / tot * 100), 1) if tot > 0 else 0
            })

        # 4. Syllabus Coverage
        total_topics_row = conn.execute("SELECT COUNT(*) as cnt FROM topics").fetchone()
        attempted_topics_row = conn.execute(
            "SELECT COUNT(DISTINCT q.topic_id) as cnt FROM attempts a JOIN questions q ON a.question_id = q.id"
        ).fetchone()
        total_questions_row = conn.execute("SELECT COUNT(*) as cnt FROM questions WHERE verified = 1").fetchone()
        attempted_q_row = conn.execute("SELECT COUNT(DISTINCT question_id) as cnt FROM attempts").fetchone()

        total_topics = total_topics_row["cnt"] or 0
        attempted_topics = attempted_topics_row["cnt"] or 0
        topic_coverage_pct = (attempted_topics / total_topics * 100) if total_topics > 0 else 0.0

        total_questions = total_questions_row["cnt"] or 0
        attempted_questions = attempted_q_row["cnt"] or 0
        question_coverage_pct = (attempted_questions / total_questions * 100) if total_questions > 0 else 0.0

        # 5. Mock Exam History
        mock_rows = conn.execute(
            """
            SELECT id, total_score, accuracy_pct, total_questions, correct_count,
                   incorrect_count, unanswered_count, time_taken_seconds, completed_at
            FROM sessions
            WHERE session_type = 'full_mock' AND is_completed = 1
            ORDER BY completed_at DESC
            LIMIT 10
            """
        ).fetchall()
        mock_history = [dict(r) for r in mock_rows]

        # 6. Fastest improving topics vs topics remaining weak
        # Compare last 7 days vs previous 7 days (7-14 days ago)
        improving_topics = []
        weakest_topics = []

        topic_perf = conn.execute(
            """
            SELECT 
                t.id, t.name as topic_name, s.name as subject_name,
                SUM(CASE WHEN a.attempted_at >= ? AND a.is_correct = 1 THEN 1 ELSE 0 END) as recent_correct,
                SUM(CASE WHEN a.attempted_at >= ? THEN 1 ELSE 0 END) as recent_total,
                SUM(CASE WHEN a.attempted_at < ? AND a.attempted_at >= ? AND a.is_correct = 1 THEN 1 ELSE 0 END) as prev_correct,
                SUM(CASE WHEN a.attempted_at < ? AND a.attempted_at >= ? THEN 1 ELSE 0 END) as prev_total
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            JOIN questions q ON q.topic_id = t.id
            JOIN attempts a ON a.question_id = q.id
            WHERE a.attempted_at >= ?
            GROUP BY t.id
            HAVING recent_total >= 3
            """,
            (seven_days_ago, seven_days_ago, seven_days_ago, fourteen_days_ago, seven_days_ago, fourteen_days_ago, fourteen_days_ago)
        ).fetchall()

        for r in topic_perf:
            rec_acc = (r["recent_correct"] / r["recent_total"]) * 100
            prev_acc = (r["prev_correct"] / r["prev_total"]) * 100 if r["prev_total"] and r["prev_total"] > 0 else rec_acc
            diff = rec_acc - prev_acc
            
            item = {
                "topic_id": r["id"],
                "topic": r["topic_name"],
                "subject": r["subject_name"],
                "recent_accuracy": round(rec_acc, 1),
                "improvement_delta": round(diff, 1)
            }
            if diff > 5:
                improving_topics.append(item)
            if rec_acc < 60:
                weakest_topics.append(item)

        improving_topics.sort(key=lambda x: x["improvement_delta"], reverse=True)
        weakest_topics.sort(key=lambda x: x["recent_accuracy"])

    # Adaptive priorities & due revisions
    adaptive_list = calculate_adaptive_priorities()
    due_revisions = get_due_revisions(limit=20)
    mistake_patterns = get_mistake_patterns()

    # Recommended next action for the 60-minute window
    top_recommended = adaptive_list[0] if adaptive_list else None
    recommended_action = {
        "title": "Daily 60-Minute Focused Plan",
        "recommended_topic": top_recommended["topic_name"] if top_recommended else "General Syllabus Practice",
        "recommended_subject": top_recommended["subject_name"] if top_recommended else "Mathematics",
        "why_recommended": top_recommended["explanation"] if top_recommended else "Begin daily practice to establish baseline accuracy.",
        "due_revisions_count": len(due_revisions),
        "suggested_breakdown": {
            "part1_review": "5 mins: Review due spaced revisions",
            "part2_practice": f"35 mins: Focused practice on {top_recommended['topic_name'] if top_recommended else 'core topics'}",
            "part3_mistake_analysis": "15 mins: Analyze incorrect answers and mistake categories",
            "part4_summary": "5 mins: Inspect accuracy improvements and plan tomorrow"
        }
    }

    # Daily 5-point honest summary
    daily_summary = {
        "what_improved": f"{improving_topics[0]['topic']} (+{improving_topics[0]['improvement_delta']}% accuracy)" if improving_topics else "Consistent practice baseline recorded.",
        "what_remains_weak": f"{weakest_topics[0]['topic']} ({weakest_topics[0]['recent_accuracy']}% accuracy)" if weakest_topics else (f"{adaptive_list[0]['topic_name']} ({adaptive_list[0]['explanation']})" if adaptive_list else "No weak topics identified yet."),
        "recurring_mistake": f"{mistake_patterns[0]['label']} ({mistake_patterns[0]['count']} occurrences)" if mistake_patterns else "No recurring mistake patterns logged yet.",
        "next_focus": f"Practice {top_recommended['topic_name']} in {top_recommended['subject_name']}" if top_recommended else "Import verified question bank to begin.",
        "session_comparison": f"Answered {answered_today} questions today with {accuracy_today:.1f}% accuracy vs {overall_accuracy:.1f}% lifetime baseline."
    }

    return {
        "answered_today": answered_today,
        "correct_today": correct_today,
        "accuracy_today": round(accuracy_today, 1),
        "time_spent_today_seconds": time_today_sec,
        "time_spent_today_minutes": round(time_today_sec / 60, 1),
        "overall_accuracy": round(overall_accuracy, 1),
        "total_attempts": total_attempts,
        "avg_solving_speed_seconds": avg_solving_speed,
        "syllabus_coverage": {
            "attempted_topics": attempted_topics,
            "total_topics": total_topics,
            "topic_coverage_pct": round(topic_coverage_pct, 1),
            "attempted_questions": attempted_questions,
            "total_questions": total_questions,
            "question_coverage_pct": round(question_coverage_pct, 1)
        },
        "daily_trend": daily_trend,
        "improving_topics": improving_topics[:5],
        "weakest_topics": weakest_topics[:5],
        "due_revisions_count": len(due_revisions),
        "mistake_patterns": mistake_patterns[:5],
        "mock_history": mock_history,
        "recommended_action": recommended_action,
        "daily_summary": daily_summary
    }
