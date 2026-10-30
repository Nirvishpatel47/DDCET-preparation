import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import pytest
from fastapi.testclient import TestClient

from app import app
from database.db import get_db, init_db
from config import derive_supabase_url_from_jwt, get_cloud_config
from services.auth_service import login_user, get_current_user, update_profile
from services.stats_service import compute_comprehensive_stats
from services.battle_service import (
    add_friend_by_email,
    remove_friend_by_email,
    compare_head_to_head,
    get_battle_leaderboard
)
from services.supabase_sync_service import (
    enqueue_stats_for_sync,
    load_sync_queue,
    save_sync_queue,
    save_friends_cache,
    load_friends_cache,
    sync_current_user_stats
)


@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path, monkeypatch):
    """Isolate SQLite database, sync queue, and cache files for each test."""
    monkeypatch.setenv("DDCET_USER_DATA_DIR", str(tmp_path))
    test_db_file = str(tmp_path / "data" / "ddcet_user.db")
    test_queue_file = str(tmp_path / "data" / "sync_queue.json")
    test_user_file = str(tmp_path / "data" / "current_user.json")
    test_cache_file = str(tmp_path / "data" / "friends_cache.json")
    test_friends_file = str(tmp_path / "data" / "friends.json")

    os.makedirs(str(tmp_path / "data"), exist_ok=True)
    os.makedirs(str(tmp_path / "backups"), exist_ok=True)

    monkeypatch.setattr("database.db.DB_PATH", test_db_file)
    monkeypatch.setattr("database.db.DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr("database.db.BACKUPS_DIR", str(tmp_path / "backups"))
    monkeypatch.setattr("config.DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr("config.BACKUPS_DIR", str(tmp_path / "backups"))
    monkeypatch.setattr("config.USER_DB_PATH", test_db_file)
    monkeypatch.setattr("config.SYNC_QUEUE_FILE", test_queue_file)
    monkeypatch.setattr("config.CURRENT_USER_FILE", test_user_file)
    monkeypatch.setattr("config.FRIENDS_FILE", test_friends_file)
    monkeypatch.setattr("config.FRIENDS_CACHE_FILE", test_cache_file)
    monkeypatch.setattr("config.ENV_PATH", str(tmp_path / ".env.test"))
    monkeypatch.setattr("services.auth_service.CURRENT_USER_FILE", test_user_file)
    monkeypatch.setattr("services.supabase_sync_service.SYNC_QUEUE_FILE", test_queue_file)
    monkeypatch.setattr("services.supabase_sync_service.FRIENDS_CACHE_FILE", test_cache_file)
    monkeypatch.setattr("services.battle_service.FRIENDS_FILE", test_friends_file)

    init_db()
    yield tmp_path


def test_jwt_url_auto_derivation():
    """Verify that project ref is extracted from Supabase JWT and URL is derived."""
    import base64
    payload = base64.b64encode(json.dumps({"iss": "supabase", "ref": "myproject123"}).encode()).decode().rstrip("=")
    fake_jwt = f"eyJhbGciOiJIUzI1NiJ9.{payload}.fake_sig"

    derived = derive_supabase_url_from_jwt(fake_jwt)
    assert derived == "https://myproject123.supabase.co"

    # Non-JWT strings return None safely
    assert derive_supabase_url_from_jwt("random_non_jwt_key") is None
    assert derive_supabase_url_from_jwt("") is None


def test_auth_login_and_profile_management():
    """Verify login, active user persistence, and profile updating."""
    client = TestClient(app)

    # 1. Default user exists
    curr = get_current_user()
    assert "email" in curr

    # 2. Login as a new student
    res = client.post("/api/auth/login", json={
        "email": "priya.patel@example.com",
        "display_name": "Priya Patel",
        "avatar": "🎯"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["email"] == "priya.patel@example.com"
    assert data["user"]["display_name"] == "Priya Patel"
    assert data["user"]["avatar"] == "🎯"

    # 3. Verify /api/auth/current
    curr_res = client.get("/api/auth/current")
    assert curr_res.status_code == 200
    assert curr_res.json()["user"]["email"] == "priya.patel@example.com"

    # 4. Profile update
    up_res = client.post("/api/auth/profile", json={
        "display_name": "Priya P. (Pro)",
        "avatar": "👑"
    })
    assert up_res.status_code == 200
    assert up_res.json()["user"]["display_name"] == "Priya P. (Pro)"
    assert up_res.json()["user"]["avatar"] == "👑"


def test_offline_sync_queueing(monkeypatch):
    """Verify that stats are stored in the local sync_queue.json file when offline."""
    monkeypatch.setattr("services.supabase_sync_service.check_internet_connection", lambda: False)
    stats = {
        "email": "offline_student@example.com",
        "display_name": "Offline Student",
        "total_questions": 45,
        "correct_count": 40,
        "accuracy_pct": 88.9,
        "total_score": 38.75
    }

    # Force unconfigured / offline sync
    res = sync_current_user_stats(stats)
    assert res["synced"] is False
    assert "queue" in res["message"].lower() or "local" in res["message"].lower()

    # Queue must contain this entry
    queue = load_sync_queue()
    assert len(queue) >= 1
    found = [q for q in queue if q["email"] == "offline_student@example.com"]
    assert len(found) == 1
    assert found[0]["total_questions"] == 45

    # Enqueueing again updates in-place without duplicating
    stats["total_questions"] = 50
    enqueue_stats_for_sync(stats)
    updated_queue = load_sync_queue()
    found_updated = [q for q in updated_queue if q["email"] == "offline_student@example.com"]
    assert len(found_updated) == 1
    assert found_updated[0]["total_questions"] == 50


def test_comprehensive_topic_wise_stats():
    """Verify that stats_service calculates topic-wise MCQs done/not done and accuracy."""
    with get_db() as conn:
        # Create subject and topics
        sub_id = conn.execute("INSERT INTO subjects (name) VALUES ('Engineering')").lastrowid
        top_id = conn.execute("INSERT INTO topics (subject_id, name) VALUES (?, 'Thermodynamics')", (sub_id,)).lastrowid
        st_id = conn.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, 'Laws')", (top_id,)).lastrowid

        # Insert 3 questions for this topic
        for i in range(1, 4):
            conn.execute(
                """
                INSERT INTO questions (id, question_text, option_a, option_b, option_c, option_d,
                                       correct_answer, explanation, subject_id, topic_id, subtopic_id,
                                       difficulty, verified, text_hash, question_text_hash, created_at)
                VALUES (?, ?, 'A', 'B', 'C', 'D', 'A', 'Expl', ?, ?, ?, 'easy', 1, ?, ?, datetime('now'))
                """,
                (f"ENG-TH-{i}", f"Thermo Question {i}", sub_id, top_id, st_id, f"th_hash_{i}", f"qh_hash_{i}")
            )

        # Create session for attempts
        conn.execute(
            """
            INSERT INTO sessions (id, session_type, total_questions, started_at)
            VALUES ('sess_1', 'daily_mixed', 2, datetime('now'))
            """
        )

        # Record 2 attempts (1 correct, 1 incorrect)
        conn.execute(
            """
            INSERT INTO attempts (question_id, session_id, selected_option, is_correct, time_spent_seconds, attempted_at)
            VALUES ('ENG-TH-1', 'sess_1', 'A', 1, 15, datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO attempts (question_id, session_id, selected_option, is_correct, time_spent_seconds, attempted_at)
            VALUES ('ENG-TH-2', 'sess_1', 'B', 0, 20, datetime('now'))
            """
        )

    stats = compute_comprehensive_stats()
    assert stats["total_questions"] == 2
    assert stats["correct_count"] == 1
    assert stats["incorrect_count"] == 1
    assert stats["total_score"] == 0.75 # 1.0 - 0.25

    # Check Topic-Wise breakdown
    t_key = "Engineering::Thermodynamics"
    assert t_key in stats["topic_stats"]
    thermo = stats["topic_stats"][t_key]
    assert thermo["total_in_bank"] == 3
    assert thermo["attempted"] == 2
    assert thermo["correct"] == 1
    assert thermo["incorrect"] == 1
    assert thermo["accuracy_pct"] == 50.0
    assert thermo["done_ratio"] == "2/3"
    assert thermo["is_done"] is False
    assert thermo["status"] == "IN_PROGRESS"


def test_battle_head_to_head_comparison():
    """Verify head-to-head battle calculations, metric duels, and topic-wise comparison matrix."""
    client = TestClient(app)

    user_stats = {
        "email": "user@example.com",
        "display_name": "Hero Cadet",
        "avatar": "⚡",
        "total_score": 50.0,
        "accuracy_pct": 85.0,
        "total_questions": 60,
        "avg_speed_seconds": 18.0,
        "topics_mastered": 5,
        "streak_days": 4,
        "topic_stats": {
            "Math::Calculus": {
                "subject": "Math",
                "topic": "Calculus",
                "total_in_bank": 20,
                "attempted": 20,
                "accuracy_pct": 90.0,
                "is_done": True,
                "mastery": "Mastered"
            },
            "Math::Trigonometry": {
                "subject": "Math",
                "topic": "Trigonometry",
                "total_in_bank": 15,
                "attempted": 8,
                "accuracy_pct": 75.0,
                "is_done": False,
                "mastery": "Proficient"
            }
        }
    }

    # Seed friend's stats in local cache
    friend_stats = {
        "email": "rival@example.com",
        "display_name": "Rival Friend",
        "avatar": "🔥",
        "total_score": 35.0,
        "accuracy_pct": 72.0,
        "total_questions": 50,
        "avg_speed_seconds": 22.0,
        "topics_mastered": 2,
        "streak_days": 2,
        "topic_stats": {
            "Math::Calculus": {
                "subject": "Math",
                "topic": "Calculus",
                "total_in_bank": 20,
                "attempted": 12,
                "accuracy_pct": 80.0,
                "is_done": False,
                "mastery": "Proficient"
            },
            "Math::Trigonometry": {
                "subject": "Math",
                "topic": "Trigonometry",
                "total_in_bank": 15,
                "attempted": 15,
                "accuracy_pct": 85.0,
                "is_done": True,
                "mastery": "Mastered"
            }
        }
    }
    save_friends_cache({"rival@example.com": friend_stats})

    # Run head-to-head comparison
    duel = compare_head_to_head(user_stats, "rival@example.com")

    assert duel["user"]["email"] == "user@example.com"
    assert duel["friend"]["email"] == "rival@example.com"
    assert duel["battle_status"] == "VICTORY" # User won score, accuracy, questions, speed, mastered
    assert duel["user"]["rounds_won"] > duel["friend"]["rounds_won"]

    # Check topic battle matrix
    calc_battle = next(t for t in duel["topic_battles"] if t["topic"] == "Calculus")
    assert calc_battle["leader"] == "YOU" # User is done with 90% vs friend 12/20 with 80%

    trig_battle = next(t for t in duel["topic_battles"] if t["topic"] == "Trigonometry")
    assert trig_battle["leader"] == "FRIEND" # Friend is done with 85% vs user 8/15 with 75%


def test_battle_api_endpoints():
    """Verify /api/battle REST endpoints: add friend, compare, leaderboard."""
    client = TestClient(app)

    # 1. Add friend by email
    add_res = client.post("/api/battle/friends", json={"friend_email": "sahil@example.com"})
    assert add_res.status_code == 200
    assert add_res.json()["success"] is True

    # 2. Friends list
    friends_res = client.get("/api/battle/friends")
    assert friends_res.status_code == 200
    emails = [f["email"] for f in friends_res.json()["friends"]]
    assert "sahil@example.com" in emails

    # 3. Head-to-head compare endpoint
    compare_res = client.get("/api/battle/compare/sahil@example.com")
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert comp_data["friend"]["email"] == "sahil@example.com"
    assert "topic_battles" in comp_data

    # 4. Leaderboard endpoint
    lb_res = client.get("/api/battle/leaderboard")
    assert lb_res.status_code == 200
    lb_data = lb_res.json()
    assert "leaderboard" in lb_data
    assert len(lb_data["leaderboard"]) >= 1

    # 5. Remove friend
    del_res = client.delete("/api/battle/friends/sahil@example.com")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True


def test_postgres_uri_isolation_from_rest(monkeypatch):
    """
    Ensure that a postgresql:// connection string in DATABASE_API_KEY is recognized
    as postgres_url and never passed as an Authorization Bearer token to PostgREST.
    """
    from services.supabase_sync_service import push_single_stats_to_supabase

    monkeypatch.setenv("DATABASE_API_KEY", "postgresql://postgres:secret@db.xyz.supabase.co:5432/postgres")
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)

    cfg = get_cloud_config()
    assert cfg["is_postgres"] is True
    assert cfg["has_rest_key"] is False
    assert cfg["api_key"] == ""
    assert cfg["postgres_url"].startswith("postgresql://")
    assert cfg["supabase_url"] == "https://xyz.supabase.co"

    # Verify that trying to sync without reachable postgres raises descriptive message
    # rather than sending a malformed HTTP Bearer request
    with pytest.raises(RuntimeError) as exc_info:
        push_single_stats_to_supabase({"email": "cadet@example.com"}, cfg)
    assert "SUPABASE_KEY" in str(exc_info.value)

