import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sqlite3
from database.db import get_db, get_all_settings


def calculate_topic_metrics(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Computes aggregated performance and revision metrics per topic directly in SQL
    for maximum efficiency even with large attempt histories.
    """
    now = datetime.utcnow()
    now_date_str = now.strftime("%Y-%m-%d")
    recent_cutoff = (now - timedelta(days=14)).isoformat()

    # Base query for all topics with their subject
    query = """
    SELECT 
        t.id as topic_id,
        t.name as topic_name,
        t.syllabus_weight,
        s.id as subject_id,
        s.name as subject_name,
        (SELECT COUNT(*) FROM questions q WHERE q.topic_id = t.id AND q.verified = 1) as total_verified_questions,
        (SELECT COUNT(DISTINCT a.question_id) FROM attempts a 
         JOIN questions q ON a.question_id = q.id 
         WHERE q.topic_id = t.id) as attempted_questions_count,
        (SELECT COUNT(*) FROM revision_schedules rs
         JOIN questions q ON rs.question_id = q.id
         WHERE q.topic_id = t.id AND rs.next_due_date <= ?) as overdue_revisions_count,
        (SELECT MAX(a.attempted_at) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id) as last_practiced_at,
        (SELECT COUNT(*) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id) as total_attempts,
        (SELECT COUNT(*) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id AND a.is_correct = 1) as total_correct,
        (SELECT COUNT(*) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id AND a.attempted_at >= ?) as recent_attempts,
        (SELECT COUNT(*) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id AND a.attempted_at >= ? AND a.is_correct = 1) as recent_correct,
        (SELECT AVG(a.time_spent_seconds) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id AND a.time_spent_seconds > 0) as avg_response_time,
        (SELECT COUNT(*) FROM attempts a
         JOIN questions q ON a.question_id = q.id
         WHERE q.topic_id = t.id AND a.mistake_category IS NOT NULL) as mistake_count
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    ORDER BY s.id, t.id
    """

    rows = conn.execute(query, (now_date_str, recent_cutoff, recent_cutoff)).fetchall()

    # Overall student baseline response time
    baseline_row = conn.execute(
        "SELECT AVG(time_spent_seconds) as baseline_time FROM attempts WHERE time_spent_seconds > 0"
    ).fetchone()
    student_baseline_time = baseline_row["baseline_time"] if baseline_row and baseline_row["baseline_time"] else 45.0

    metrics = []
    for r in rows:
        total_verified = r["total_verified_questions"]
        attempted = r["attempted_questions_count"]
        unseen_count = max(0, total_verified - attempted)
        
        last_dt = None
        days_since_practice = 30 # default if never practiced
        if r["last_practiced_at"]:
            try:
                last_dt = datetime.fromisoformat(r["last_practiced_at"].replace("Z", "+00:00").split("+")[0])
                days_since_practice = (now - last_dt).days
            except Exception:
                days_since_practice = 14

        metrics.append({
            "topic_id": r["topic_id"],
            "topic_name": r["topic_name"],
            "subject_id": r["subject_id"],
            "subject_name": r["subject_name"],
            "syllabus_weight": float(r["syllabus_weight"] or 1.0),
            "total_verified": total_verified,
            "unseen_count": unseen_count,
            "overdue_revisions": r["overdue_revisions_count"],
            "last_practiced_at": r["last_practiced_at"],
            "days_since_practice": max(0, days_since_practice),
            "total_attempts": r["total_attempts"],
            "total_correct": r["total_correct"],
            "recent_attempts": r["recent_attempts"],
            "recent_correct": r["recent_correct"],
            "avg_response_time": float(r["avg_response_time"]) if r["avg_response_time"] else 0.0,
            "mistake_count": r["mistake_count"],
            "student_baseline_time": float(student_baseline_time)
        })

    return metrics


def calculate_adaptive_priorities() -> List[Dict[str, Any]]:
    """
    Applies the rule-based formula:
    priority = w_weakness * weakness_score +
               w_revision * revision_urgency +
               w_syllabus * syllabus_importance +
               w_neglect  * neglect_score +
               w_speed    * speed_difficulty_score
    Returns topics ordered by priority descending, with full transparent breakdowns and explanations.
    """
    settings = get_all_settings()
    w_weak = float(settings.get("priority_weight_weakness", 0.35))
    w_rev = float(settings.get("priority_weight_revision", 0.25))
    w_syl = float(settings.get("priority_weight_syllabus", 0.20))
    w_neg = float(settings.get("priority_weight_neglect", 0.10))
    w_spd = float(settings.get("priority_weight_speed", 0.10))

    # Normalize weights if user adjusted them and sum != 1.0
    w_sum = w_weak + w_rev + w_syl + w_neg + w_spd
    if w_sum > 0:
        w_weak /= w_sum
        w_rev /= w_sum
        w_syl /= w_sum
        w_neg /= w_sum
        w_spd /= w_sum

    with get_db() as conn:
        topic_metrics = calculate_topic_metrics(conn)

    if not topic_metrics:
        return []

    # Maximums for normalization
    max_syllabus = max((m["syllabus_weight"] for m in topic_metrics), default=1.0)
    max_syllabus = max(max_syllabus, 1.0)
    max_overdue = max((m["overdue_revisions"] for m in topic_metrics), default=1)
    max_overdue = max(max_overdue, 1)

    results = []
    for m in topic_metrics:
        is_diagnostic = False
        tot_att = m["total_attempts"]
        rec_att = m["recent_attempts"]
        rec_cor = m["recent_correct"]
        
        # 1. Weakness Score with Laplace/Bayesian smoothing:
        # If no attempts yet: this is a new topic, needs diagnostic questions rather than marking weak.
        # Smoothing formula: (incorrect + 1) / (attempts + 2)
        if tot_att == 0:
            is_diagnostic = True
            weakness_score = 0.50 # Neutral prior
            reason_weakness = "New topic with no prior attempts. Queued for diagnostic evaluation."
        else:
            # Use recent attempts if >= 3, else all attempts
            att_to_use = rec_att if rec_att >= 3 else tot_att
            cor_to_use = rec_cor if rec_att >= 3 else m["total_correct"]
            inc_to_use = att_to_use - cor_to_use
            # Smoothed error rate:
            weakness_score = (inc_to_use + 1.0) / (att_to_use + 2.0)
            actual_acc = (cor_to_use / att_to_use) * 100 if att_to_use > 0 else 0
            reason_weakness = f"Recent accuracy is {actual_acc:.0f}% ({cor_to_use}/{att_to_use} correct)."

        # 2. Revision Urgency:
        # Overdue revisions normalized to 0-1
        rev_count = m["overdue_revisions"]
        revision_urgency = min(1.0, rev_count / float(max_overdue))
        if rev_count > 0:
            reason_revision = f"{rev_count} questions currently overdue for spaced revision."
        else:
            reason_revision = "No overdue spaced revisions."

        # 3. Syllabus Importance:
        syllabus_importance = min(1.0, m["syllabus_weight"] / max_syllabus)
        reason_syllabus = f"Syllabus weight factor: {m['syllabus_weight']}x."

        # 4. Neglect Score:
        # 0 to 1 based on days since practice, capped at 14 days
        days = m["days_since_practice"]
        neglect_score = min(1.0, days / 14.0)
        if tot_att == 0:
            reason_neglect = "Never practiced yet."
        else:
            reason_neglect = f"Last practiced {days} days ago."

        # 5. Speed Difficulty Score:
        # High solving time relative to student's own baseline indicates struggling topic
        avg_time = m["avg_response_time"]
        baseline = m["student_baseline_time"]
        if avg_time > 0 and baseline > 0:
            ratio = avg_time / baseline
            # Normalize: 0.5 baseline = 0.0, 2.0x baseline = 1.0
            speed_score = min(1.0, max(0.0, (ratio - 0.5) / 1.5))
            reason_speed = f"Average solving time ({avg_time:.1f}s) is {ratio:.1f}x baseline ({baseline:.1f}s)."
        else:
            speed_score = 0.30
            reason_speed = "Standard baseline speed applied."

        # Final Weighted Priority Score
        priority = (
            w_weak * weakness_score +
            w_rev * revision_urgency +
            w_syl * syllabus_importance +
            w_neg * neglect_score +
            w_spd * speed_score
        )

        # Human-readable "Why this was prioritized" explanation
        reasons = []
        if rev_count > 0:
            reasons.append(reason_revision)
        if weakness_score > 0.6:
            reasons.append(reason_weakness)
        if neglect_score > 0.5:
            reasons.append(reason_neglect)
        if is_diagnostic:
            reasons.append("New syllabus topic: diagnostic questions needed to map baseline.")
        if not reasons:
            reasons.append(f"Standard balanced syllabus priority ({m['subject_name']}).")

        explanation_str = " | ".join(reasons)

        results.append({
            "topic_id": m["topic_id"],
            "topic_name": m["topic_name"],
            "subject_id": m["subject_id"],
            "subject_name": m["subject_name"],
            "priority": round(priority, 4),
            "is_diagnostic": is_diagnostic,
            "components": {
                "weakness_score": round(weakness_score, 3),
                "revision_urgency": round(revision_urgency, 3),
                "syllabus_importance": round(syllabus_importance, 3),
                "neglect_score": round(neglect_score, 3),
                "speed_difficulty_score": round(speed_score, 3)
            },
            "weights_used": {
                "weakness": round(w_weak, 2),
                "revision": round(w_rev, 2),
                "syllabus": round(w_syl, 2),
                "neglect": round(w_neg, 2),
                "speed": round(w_spd, 2)
            },
            "explanation": explanation_str,
            "metrics": m
        })

    results.sort(key=lambda x: x["priority"], reverse=True)
    return results
