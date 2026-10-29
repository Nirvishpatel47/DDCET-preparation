import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from config import DATA_DIR
from services.auth_service import get_current_user
from services.stats_service import compute_comprehensive_stats
from services.supabase_sync_service import (
    fetch_friend_stats_from_cloud_or_cache,
    fetch_leaderboard_from_cloud_or_cache,
    save_friends_cache,
    load_friends_cache
)

FRIENDS_FILE = os.path.join(DATA_DIR, "friends.json")


def load_friends_data() -> List[str]:
    """Loads saved friends email list from local JSON file."""
    if os.path.isfile(FRIENDS_FILE):
        try:
            with open(FRIENDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [e.strip().lower() for e in data if isinstance(e, str) and e.strip()]
        except Exception as e:
            print(f"[battle_service] Error reading friends file: {e}")
    return []


def save_friends_data(friends: List[str]):
    """Saves friends list to local JSON file."""
    try:
        with open(FRIENDS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(dict.fromkeys(friends)), f, indent=2)
    except Exception as e:
        print(f"[battle_service] Error writing friends file: {e}")


def add_friend_by_email(friend_email: str) -> Dict[str, Any]:
    """
    Adds a friend by email, searches for their stats in cloud or cache,
    and returns their profile summary.
    """
    clean_email = friend_email.strip().lower()
    user = get_current_user()
    user_email = user.get("email", "").strip().lower()

    if not clean_email or "@" not in clean_email:
        raise ValueError("Please provide a valid friend's email address.")

    if clean_email == user_email:
        raise ValueError("You cannot add yourself as a competitor friend.")

    friends = load_friends_data()
    if clean_email not in friends:
        friends.append(clean_email)
        save_friends_data(friends)

    # Fetch stats for this friend
    friend_stats = fetch_friend_stats_from_cloud_or_cache(clean_email)
    
    # If friend stats not found yet on cloud, create a placeholder in cache
    if not friend_stats:
        cache = load_friends_cache()
        placeholder = {
            "email": clean_email,
            "display_name": clean_email.split("@")[0].capitalize(),
            "avatar": "👤",
            "total_questions": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "accuracy_pct": 0.0,
            "total_score": 0.0,
            "study_time_minutes": 0.0,
            "streak_days": 0,
            "avg_speed_seconds": 0.0,
            "topics_mastered": 0,
            "topics_total": 0,
            "topic_stats": {},
            "mock_stats": [],
            "source": "placeholder_unregistered",
            "last_active": datetime.utcnow().isoformat()
        }
        cache[clean_email] = placeholder
        save_friends_cache(cache)
        friend_stats = placeholder

    return {
        "success": True,
        "message": f"Added friend {clean_email} to Battle Competitors.",
        "friend": friend_stats
    }


def remove_friend_by_email(friend_email: str) -> bool:
    """Removes a friend from local competitors list."""
    clean_email = friend_email.strip().lower()
    friends = load_friends_data()
    if clean_email in friends:
        friends.remove(clean_email)
        save_friends_data(friends)
        return True
    return False


def get_all_friends_with_stats() -> List[Dict[str, Any]]:
    """Returns all friends with their latest available stats."""
    friends = load_friends_data()
    result = []
    
    for f_email in friends:
        f_stats = fetch_friend_stats_from_cloud_or_cache(f_email)
        if f_stats:
            result.append(f_stats)
        else:
            result.append({
                "email": f_email,
                "display_name": f_email.split("@")[0].capitalize(),
                "avatar": "👤",
                "total_questions": 0,
                "accuracy_pct": 0.0,
                "total_score": 0.0,
                "topics_mastered": 0,
                "source": "unregistered"
            })
    
    return result


def compare_head_to_head(user_stats: Dict[str, Any], friend_email: str) -> Dict[str, Any]:
    """
    Computes a detailed, battle-grade head-to-head comparison between current user
    and friend, featuring overall metric duels and granular Topic-Wise MCQs done/not done.
    """
    clean_email = friend_email.strip().lower()
    friend_stats = fetch_friend_stats_from_cloud_or_cache(clean_email)

    if not friend_stats:
        # Check if friend is in friends list
        add_friend_by_email(clean_email)
        friend_stats = fetch_friend_stats_from_cloud_or_cache(clean_email)

    if not friend_stats:
        raise ValueError(f"Could not load stats for friend '{clean_email}'.")

    # 1. Overall Metrics Comparison Duel
    user_score = float(user_stats.get("total_score") or 0.0)
    friend_score = float(friend_stats.get("total_score") or 0.0)
    
    user_acc = float(user_stats.get("accuracy_pct") or 0.0)
    friend_acc = float(friend_stats.get("accuracy_pct") or 0.0)

    user_q = int(user_stats.get("total_questions") or 0)
    friend_q = int(friend_stats.get("total_questions") or 0)

    user_speed = float(user_stats.get("avg_speed_seconds") or 0.0)
    friend_speed = float(friend_stats.get("avg_speed_seconds") or 0.0)

    user_mastered = int(user_stats.get("topics_mastered") or 0)
    friend_mastered = int(friend_stats.get("topics_mastered") or 0)

    user_streak = int(user_stats.get("streak_days") or 1)
    friend_streak = int(friend_stats.get("streak_days") or 0)

    # Points tally (rounds won)
    user_rounds_won = 0
    friend_rounds_won = 0

    if user_score > friend_score:
        user_rounds_won += 1
    elif friend_score > user_score:
        friend_rounds_won += 1

    if user_acc > friend_acc:
        user_rounds_won += 1
    elif friend_acc > user_acc:
        friend_rounds_won += 1

    if user_q > friend_q:
        user_rounds_won += 1
    elif friend_q > user_q:
        friend_rounds_won += 1

    if user_speed > 0 and friend_speed > 0:
        if user_speed < friend_speed: # faster is better
            user_rounds_won += 1
        elif friend_speed < user_speed:
            friend_rounds_won += 1

    if user_mastered > friend_mastered:
        user_rounds_won += 1
    elif friend_mastered > user_mastered:
        friend_rounds_won += 1

    metrics_comparison = [
        {
            "metric": "Total Score",
            "user_val": user_score,
            "friend_val": friend_score,
            "user_display": f"{user_score:+.2f}",
            "friend_display": f"{friend_score:+.2f}",
            "winner": "YOU" if user_score > friend_score else ("FRIEND" if friend_score > user_score else "TIE"),
            "diff": round(abs(user_score - friend_score), 2)
        },
        {
            "metric": "Overall Accuracy",
            "user_val": user_acc,
            "friend_val": friend_acc,
            "user_display": f"{user_acc:.1f}%",
            "friend_display": f"{friend_acc:.1f}%",
            "winner": "YOU" if user_acc > friend_acc else ("FRIEND" if friend_acc > user_acc else "TIE"),
            "diff": round(abs(user_acc - friend_acc), 1)
        },
        {
            "metric": "Questions Solved",
            "user_val": user_q,
            "friend_val": friend_q,
            "user_display": f"{user_q} MCQs",
            "friend_display": f"{friend_q} MCQs",
            "winner": "YOU" if user_q > friend_q else ("FRIEND" if friend_q > user_q else "TIE"),
            "diff": abs(user_q - friend_q)
        },
        {
            "metric": "Solving Speed",
            "user_val": user_speed,
            "friend_val": friend_speed,
            "user_display": f"{user_speed:.1f}s/q",
            "friend_display": f"{friend_speed:.1f}s/q",
            "winner": "YOU" if (0 < user_speed < friend_speed) else ("FRIEND" if (0 < friend_speed < user_speed) else "TIE"),
            "diff": round(abs(user_speed - friend_speed), 1)
        },
        {
            "metric": "Topics Mastered",
            "user_val": user_mastered,
            "friend_val": friend_mastered,
            "user_display": f"{user_mastered} Topics",
            "friend_display": f"{friend_mastered} Topics",
            "winner": "YOU" if user_mastered > friend_mastered else ("FRIEND" if friend_mastered > user_mastered else "TIE"),
            "diff": abs(user_mastered - friend_mastered)
        },
        {
            "metric": "Daily Streak",
            "user_val": user_streak,
            "friend_val": friend_streak,
            "user_display": f"{user_streak} Days 🔥",
            "friend_display": f"{friend_streak} Days 🔥",
            "winner": "YOU" if user_streak > friend_streak else ("FRIEND" if friend_streak > user_streak else "TIE"),
            "diff": abs(user_streak - friend_streak)
        }
    ]

    # 2. Granular Topic-Wise MCQs Done / Not Done Battle Matrix
    user_topics: Dict[str, Any] = user_stats.get("topic_stats") or {}
    friend_topics: Dict[str, Any] = friend_stats.get("topic_stats") or {}

    # Union of all topic keys
    all_topic_keys = sorted(set(list(user_topics.keys()) + list(friend_topics.keys())))

    topic_battles = []
    user_topic_wins = 0
    friend_topic_wins = 0
    tied_topic_count = 0

    for t_key in all_topic_keys:
        u_t = user_topics.get(t_key, {})
        f_t = friend_topics.get(t_key, {})

        subj = u_t.get("subject") or f_t.get("subject") or t_key.split("::")[0]
        topic_name = u_t.get("topic") or f_t.get("topic") or (t_key.split("::")[1] if "::" in t_key else t_key)
        total_in_bank = u_t.get("total_in_bank") or f_t.get("total_in_bank") or 0

        u_att = u_t.get("attempted", 0)
        u_acc = u_t.get("accuracy_pct", 0.0)
        u_done = u_t.get("is_done", False)
        u_mastery = u_t.get("mastery", "Untested")
        u_ratio = f"{u_att}/{total_in_bank}"

        f_att = f_t.get("attempted", 0)
        f_acc = f_t.get("accuracy_pct", 0.0)
        f_done = f_t.get("is_done", False)
        f_mastery = f_t.get("mastery", "Untested")
        f_ratio = f"{f_att}/{total_in_bank}"

        # Evaluate Topic Leader
        if u_att == 0 and f_att == 0:
            leader = "NEITHER"
            leader_label = "Untested ⚪"
        elif u_done and not f_done:
            leader = "YOU"
            leader_label = "You Lead 🏆"
            user_topic_wins += 1
        elif f_done and not u_done:
            leader = "FRIEND"
            leader_label = f"{friend_stats['display_name']} Leads 🔥"
            friend_topic_wins += 1
        elif u_acc > f_acc:
            leader = "YOU"
            leader_label = "You Lead 🏆"
            user_topic_wins += 1
        elif f_acc > u_acc:
            leader = "FRIEND"
            leader_label = f"{friend_stats['display_name']} Leads 🔥"
            friend_topic_wins += 1
        elif u_att > f_att:
            leader = "YOU"
            leader_label = "You Lead 🏆"
            user_topic_wins += 1
        elif f_att > u_att:
            leader = "FRIEND"
            leader_label = f"{friend_stats['display_name']} Leads 🔥"
            friend_topic_wins += 1
        else:
            leader = "TIED"
            leader_label = "Tied 🤝"
            tied_topic_count += 1

        topic_battles.append({
            "topic_key": t_key,
            "subject": subj,
            "topic": topic_name,
            "total_in_bank": total_in_bank,
            "user": {
                "attempted": u_att,
                "done_ratio": u_ratio,
                "is_done": u_done,
                "accuracy_pct": u_acc,
                "mastery": u_mastery
            },
            "friend": {
                "attempted": f_att,
                "done_ratio": f_ratio,
                "is_done": f_done,
                "accuracy_pct": f_acc,
                "mastery": f_mastery
            },
            "leader": leader,
            "leader_label": leader_label
        })

    # Overall Battle Verdict
    if user_rounds_won > friend_rounds_won:
        battle_status = "VICTORY"
        verdict_title = f"👑 You are Leading the Battle ({user_rounds_won} - {friend_rounds_won})"
        verdict_desc = f"You are dominating in {user_rounds_won} core metric categories and lead in {user_topic_wins} individual syllabus topics!"
    elif friend_rounds_won > user_rounds_won:
        battle_status = "DEFEAT"
        verdict_title = f"⚔️ {friend_stats['display_name']} is Leading ({friend_rounds_won} - {user_rounds_won})"
        verdict_desc = f"{friend_stats['display_name']} holds the advantage in {friend_rounds_won} categories. Solve more MCQs to overtake them!"
    else:
        battle_status = "DRAW"
        verdict_title = f"🤝 Dead Even Tie ({user_rounds_won} - {friend_rounds_won})"
        verdict_desc = "Intense competition! You and your friend are neck and neck across all performance metrics."

    return {
        "user": {
            "email": user_stats.get("email"),
            "display_name": user_stats.get("display_name"),
            "avatar": user_stats.get("avatar"),
            "rounds_won": user_rounds_won,
            "topics_won": user_topic_wins
        },
        "friend": {
            "email": friend_stats.get("email"),
            "display_name": friend_stats.get("display_name"),
            "avatar": friend_stats.get("avatar"),
            "rounds_won": friend_rounds_won,
            "topics_won": friend_topic_wins,
            "source": friend_stats.get("source", "cache")
        },
        "battle_status": battle_status,
        "verdict_title": verdict_title,
        "verdict_desc": verdict_desc,
        "metrics_comparison": metrics_comparison,
        "topic_battles": topic_battles,
        "summary": {
            "user_rounds": user_rounds_won,
            "friend_rounds": friend_rounds_won,
            "user_topics_won": user_topic_wins,
            "friend_topics_won": friend_topic_wins,
            "tied_topics": tied_topic_count,
            "total_topics_contested": len(all_topic_keys)
        }
    }


def get_battle_leaderboard() -> List[Dict[str, Any]]:
    """
    Returns full leaderboard combining local user + all friends + cloud competitors.
    Ranked by total_score descending.
    """
    user_stats = compute_comprehensive_stats()
    friends = get_all_friends_with_stats()

    combined: Dict[str, Dict[str, Any]] = {}
    
    # 1. Add friends
    for f in friends:
        if f.get("email"):
            combined[f["email"]] = f

    # 2. Add current user
    user_email = user_stats.get("email")
    if user_email:
        combined[user_email] = user_stats

    # 3. Add any cloud entries
    cloud_entries = fetch_leaderboard_from_cloud_or_cache()
    for c in cloud_entries:
        c_email = c.get("email")
        if c_email and c_email not in combined:
            combined[c_email] = c

    # Sort by total_score descending
    ranked_list = list(combined.values())
    ranked_list.sort(key=lambda x: float(x.get("total_score") or 0.0), reverse=True)

    # Assign ranks
    for idx, item in enumerate(ranked_list):
        item["rank"] = idx + 1
        item["is_current_user"] = (item.get("email") == user_email)

    return ranked_list
