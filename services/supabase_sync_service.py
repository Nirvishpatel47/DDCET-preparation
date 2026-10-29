import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

from config import get_cloud_config, SYNC_QUEUE_FILE, FRIENDS_CACHE_FILE
from services.auth_service import get_current_user


def load_sync_queue() -> List[Dict[str, Any]]:
    """Loads the list of pending sync items from local JSON file."""
    if os.path.isfile(SYNC_QUEUE_FILE):
        try:
            with open(SYNC_QUEUE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"[sync_service] Error reading sync queue: {e}")
    return []


def save_sync_queue(queue: List[Dict[str, Any]]):
    """Persists the sync queue to local JSON file."""
    try:
        with open(SYNC_QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        print(f"[sync_service] Error writing sync queue: {e}")


def enqueue_stats_for_sync(stats_payload: Dict[str, Any]):
    """
    Enqueues stats for sync. If an entry for the same user already exists in the queue,
    it updates it with the latest stats to keep the queue minimal and efficient.
    """
    queue = load_sync_queue()
    email = stats_payload.get("email")
    updated = False
    
    for item in queue:
        if item.get("email") == email:
            item.update(stats_payload)
            item["queued_at"] = datetime.utcnow().isoformat()
            updated = True
            break

    if not updated:
        stats_payload["queued_at"] = datetime.utcnow().isoformat()
        queue.append(stats_payload)

    save_sync_queue(queue)


def load_friends_cache() -> Dict[str, Dict[str, Any]]:
    """Loads cached friends stats for offline viewing."""
    if os.path.isfile(FRIENDS_CACHE_FILE):
        try:
            with open(FRIENDS_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[sync_service] Error reading friends cache: {e}")
    return {}


def save_friends_cache(cache: Dict[str, Dict[str, Any]]):
    """Persists friends cache locally."""
    try:
        with open(FRIENDS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"[sync_service] Error writing friends cache: {e}")


def check_internet_connection(timeout: float = 2.0) -> bool:
    """
    Checks if internet is accessible.
    First checks Supabase if configured, otherwise falls back to a fast public endpoint.
    """
    cfg = get_cloud_config()
    target_url = cfg["supabase_url"] if (cfg["is_configured"] and cfg["supabase_url"]) else "https://1.1.1.1"

    try:
        with httpx.Client(timeout=timeout) as client:
            client.get(target_url)
            return True
    except Exception:
        # Fallback check
        try:
            with httpx.Client(timeout=1.0) as client:
                client.get("https://www.google.com")
                return True
        except Exception:
            return False


def get_supabase_headers(cfg: Dict[str, Any]) -> Dict[str, str]:
    api_key = cfg["api_key"]
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }


def push_stats_via_postgres(stats_payload: Dict[str, Any], postgres_conn_str: str) -> bool:
    """Pushes user stats and profile directly to PostgreSQL via psycopg2."""
    import psycopg2
    from psycopg2.extras import Json

    conn = psycopg2.connect(postgres_conn_str, connect_timeout=3)
    try:
        with conn.cursor() as cur:
            # Ensure tables exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.ddcet_profiles (
                    email TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    avatar TEXT DEFAULT '⚡',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS public.ddcet_user_stats (
                    email TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    avatar TEXT DEFAULT '⚡',
                    total_questions INTEGER NOT NULL DEFAULT 0,
                    correct_count INTEGER NOT NULL DEFAULT 0,
                    incorrect_count INTEGER NOT NULL DEFAULT 0,
                    accuracy_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
                    total_score NUMERIC(7, 2) NOT NULL DEFAULT 0.00,
                    study_time_minutes NUMERIC(7, 1) NOT NULL DEFAULT 0.0,
                    streak_days INTEGER NOT NULL DEFAULT 1,
                    avg_speed_seconds NUMERIC(6, 1) NOT NULL DEFAULT 0.0,
                    topics_mastered INTEGER NOT NULL DEFAULT 0,
                    topics_total INTEGER NOT NULL DEFAULT 0,
                    topic_stats JSONB NOT NULL DEFAULT '{}'::jsonb,
                    mock_stats JSONB NOT NULL DEFAULT '[]'::jsonb,
                    last_active TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS public.ddcet_friends (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    friend_email TEXT NOT NULL,
                    added_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(user_email, friend_email)
                );
            """)

            # Upsert Profile
            cur.execute("""
                INSERT INTO public.ddcet_profiles (email, display_name, avatar, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (email) DO UPDATE
                SET display_name = EXCLUDED.display_name,
                    avatar = EXCLUDED.avatar,
                    updated_at = NOW();
            """, (stats_payload["email"], stats_payload.get("display_name", "Student"), stats_payload.get("avatar", "⚡")))

            # Upsert Stats
            cur.execute("""
                INSERT INTO public.ddcet_user_stats (
                    email, display_name, avatar, total_questions, correct_count, incorrect_count,
                    accuracy_pct, total_score, study_time_minutes, streak_days, avg_speed_seconds,
                    topics_mastered, topics_total, topic_stats, mock_stats, last_active, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
                ON CONFLICT (email) DO UPDATE
                SET display_name = EXCLUDED.display_name,
                    avatar = EXCLUDED.avatar,
                    total_questions = EXCLUDED.total_questions,
                    correct_count = EXCLUDED.correct_count,
                    incorrect_count = EXCLUDED.incorrect_count,
                    accuracy_pct = EXCLUDED.accuracy_pct,
                    total_score = EXCLUDED.total_score,
                    study_time_minutes = EXCLUDED.study_time_minutes,
                    streak_days = EXCLUDED.streak_days,
                    avg_speed_seconds = EXCLUDED.avg_speed_seconds,
                    topics_mastered = EXCLUDED.topics_mastered,
                    topics_total = EXCLUDED.topics_total,
                    topic_stats = EXCLUDED.topic_stats,
                    mock_stats = EXCLUDED.mock_stats,
                    last_active = NOW(),
                    updated_at = NOW();
            """, (
                stats_payload["email"],
                stats_payload.get("display_name", "Student"),
                stats_payload.get("avatar", "⚡"),
                stats_payload.get("total_questions", 0),
                stats_payload.get("correct_count", 0),
                stats_payload.get("incorrect_count", 0),
                stats_payload.get("accuracy_pct", 0.0),
                stats_payload.get("total_score", 0.0),
                stats_payload.get("study_time_minutes", 0.0),
                stats_payload.get("streak_days", 1),
                stats_payload.get("avg_speed_seconds", 0.0),
                stats_payload.get("topics_mastered", 0),
                stats_payload.get("topics_total", 0),
                Json(stats_payload.get("topic_stats", {})),
                Json(stats_payload.get("mock_stats", [])),
            ))
        conn.commit()
        return True
    finally:
        conn.close()


def push_single_stats_to_supabase(stats_payload: Dict[str, Any], cfg: Dict[str, Any]) -> bool:
    """Pushes a user's stats and profile to Supabase (via PostgreSQL direct connection or REST API)."""
    pg_err_msg = None

    # 1. If direct PostgreSQL connection string provided
    if cfg.get("postgres_url"):
        try:
            return push_stats_via_postgres(stats_payload, cfg["postgres_url"])
        except Exception as pg_err:
            pg_err_msg = str(pg_err)
            print(f"[sync_service] Direct postgres sync notice: {pg_err}")
            # If postgres direct fails, continue to REST check or raise to queue locally

    # 2. REST API fallback if Supabase URL and anon/service key available
    if cfg.get("has_rest_key") and cfg.get("supabase_url"):
        supabase_url = cfg["supabase_url"]
        headers = get_supabase_headers(cfg)

        profile_data = {
            "email": stats_payload["email"],
            "display_name": stats_payload.get("display_name", "Student"),
            "avatar": stats_payload.get("avatar", "⚡"),
            "updated_at": datetime.utcnow().isoformat()
        }

        stats_data = {
            "email": stats_payload["email"],
            "display_name": stats_payload.get("display_name", "Student"),
            "avatar": stats_payload.get("avatar", "⚡"),
            "total_questions": stats_payload.get("total_questions", 0),
            "correct_count": stats_payload.get("correct_count", 0),
            "incorrect_count": stats_payload.get("incorrect_count", 0),
            "accuracy_pct": stats_payload.get("accuracy_pct", 0.0),
            "total_score": stats_payload.get("total_score", 0.0),
            "study_time_minutes": stats_payload.get("study_time_minutes", 0.0),
            "streak_days": stats_payload.get("streak_days", 1),
            "avg_speed_seconds": stats_payload.get("avg_speed_seconds", 0.0),
            "topics_mastered": stats_payload.get("topics_mastered", 0),
            "topics_total": stats_payload.get("topics_total", 0),
            "topic_stats": stats_payload.get("topic_stats", {}),
            "mock_stats": stats_payload.get("mock_stats", []),
            "last_active": stats_payload.get("last_active", datetime.utcnow().isoformat()),
            "updated_at": datetime.utcnow().isoformat()
        }

        try:
            with httpx.Client(timeout=4.0) as client:
                p_resp = client.post(
                    f"{supabase_url}/rest/v1/ddcet_profiles",
                    json=profile_data,
                    headers=headers
                )
                if p_resp.status_code == 404:
                    raise RuntimeError(
                        "Tables not found in Supabase. Please open Supabase SQL Editor and run 'database/supabase_schema.sql' to create the required tables."
                    )
                p_resp.raise_for_status()

                resp = client.post(
                    f"{supabase_url}/rest/v1/ddcet_user_stats",
                    json=stats_data,
                    headers=headers
                )
                if resp.status_code == 404:
                    raise RuntimeError(
                        "Table 'ddcet_user_stats' not found in Supabase. Please open Supabase SQL Editor and run 'database/supabase_schema.sql' to create the tables."
                    )
                resp.raise_for_status()

            return True
        except httpx.HTTPStatusError as http_err:
            if http_err.response.status_code == 404:
                raise RuntimeError(
                    "Table not found in Supabase. Please run 'database/supabase_schema.sql' in your Supabase SQL Editor."
                ) from http_err
            raise

    if pg_err_msg:
        raise RuntimeError(
            f"Direct PostgreSQL connection failed ({pg_err_msg}). "
            "To enable instant HTTPS sync, please add your Supabase 'anon' public key to .env: SUPABASE_KEY=your_anon_key"
        )

    raise RuntimeError("No valid Supabase credentials configured. Please add SUPABASE_KEY to .env.")


def sync_pending_queue() -> Dict[str, Any]:
    """
    Attempts to push all pending stats from the local JSON queue to Supabase.
    If offline or unconfigured, preserves queue intact.
    """
    cfg = get_cloud_config()
    queue = load_sync_queue()

    if not queue:
        return {
            "status": "idle",
            "synced_count": 0,
            "remaining_count": 0,
            "message": "Sync queue is empty."
        }

    if not cfg["is_configured"]:
        return {
            "status": "unconfigured",
            "synced_count": 0,
            "remaining_count": len(queue),
            "message": "DATABASE_API_KEY is not configured yet in .env."
        }

    if not check_internet_connection():
        return {
            "status": "offline",
            "synced_count": 0,
            "remaining_count": len(queue),
            "message": "No internet connection. Stats remain queued safely in local JSON file."
        }

    synced_items = []
    failed_items = []

    for item in queue:
        try:
            push_single_stats_to_supabase(item, cfg)
            synced_items.append(item)
        except Exception as e:
            print(f"[sync_service] Failed to push stats for {item.get('email')}: {e}")
            failed_items.append(item)

    save_sync_queue(failed_items)

    return {
        "status": "success" if not failed_items else "partial",
        "synced_count": len(synced_items),
        "remaining_count": len(failed_items),
        "message": f"Successfully synced {len(synced_items)} updates to Supabase."
    }


def sync_current_user_stats(stats_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main sync gateway:
    1. Always stores/updates latest stats in local queue or cache.
    2. If online and Supabase configured, pushes immediately and clears queue.
    3. If offline, stores inside local .json file and marks status as offline_queued.
    """
    cfg = get_cloud_config()
    enqueue_stats_for_sync(stats_payload)

    if not cfg["is_configured"]:
        return {
            "synced": False,
            "status": "unconfigured",
            "message": "Saved to local JSON queue. Add DATABASE_API_KEY to .env to enable Cloud Sync."
        }

    # Attempt immediate sync
    if check_internet_connection():
        try:
            push_single_stats_to_supabase(stats_payload, cfg)
            # Remove from queue if pushed
            queue = load_sync_queue()
            email = stats_payload.get("email")
            queue = [q for q in queue if q.get("email") != email]
            save_sync_queue(queue)
            
            # Also flush any older pending items
            sync_pending_queue()

            return {
                "synced": True,
                "status": "online_synced",
                "message": "Stats successfully synced to Supabase Cloud."
            }
        except Exception as e:
            return {
                "synced": False,
                "status": "error_queued",
                "message": f"Sync queued locally: {e}."
            }

    return {
        "synced": False,
        "status": "offline_queued",
        "message": "No internet connection. Stats stored in local JSON queue and will push when online."
    }


def fetch_friend_via_postgres(friend_email: str, postgres_conn_str: str) -> Optional[Dict[str, Any]]:
    """Queries a friend's stats directly from PostgreSQL."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(postgres_conn_str, connect_timeout=3)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM public.ddcet_user_stats WHERE email = %s", (friend_email,))
            row = cur.fetchone()
            if row:
                res = dict(row)
                res["source"] = "cloud_live"
                return res
            return None
    finally:
        conn.close()


def fetch_leaderboard_via_postgres(postgres_conn_str: str) -> List[Dict[str, Any]]:
    """Queries top competitors directly from PostgreSQL."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(postgres_conn_str, connect_timeout=3)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM public.ddcet_user_stats ORDER BY total_score DESC LIMIT 25")
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def fetch_friend_stats_from_cloud_or_cache(friend_email: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a friend's stats by their email:
    1. If online + configured: fetches fresh stats from Supabase and updates local cache.
    2. If offline / error: reads from local friends_cache.json.
    """
    clean_email = friend_email.strip().lower()
    cache = load_friends_cache()
    cfg = get_cloud_config()

    if cfg["is_configured"] and check_internet_connection():
        # Try direct PostgreSQL if URL is provided
        if cfg.get("postgres_url"):
            try:
                friend_data = fetch_friend_via_postgres(clean_email, cfg["postgres_url"])
                if friend_data:
                    friend_data["cached_at"] = datetime.utcnow().isoformat()
                    cache[clean_email] = friend_data
                    save_friends_cache(cache)
                    return friend_data
            except Exception as e:
                print(f"[sync_service] Error querying postgres friend stats: {e}")

        # Try REST fallback if valid API key and Supabase URL available
        if cfg.get("has_rest_key") and cfg.get("supabase_url"):
            try:
                supabase_url = cfg["supabase_url"]
                headers = get_supabase_headers(cfg)

                with httpx.Client(timeout=3.0) as client:
                    url = f"{supabase_url}/rest/v1/ddcet_user_stats?email=eq.{clean_email}&select=*"
                    resp = client.get(url, headers=headers)
                    if resp.status_code == 200:
                        rows = resp.json()
                        if rows and len(rows) > 0:
                            friend_data = rows[0]
                            friend_data["source"] = "cloud_live"
                            friend_data["cached_at"] = datetime.utcnow().isoformat()
                            cache[clean_email] = friend_data
                            save_friends_cache(cache)
                            return friend_data
            except Exception as e:
                print(f"[sync_service] Error querying cloud friend stats: {e}")

    # Fallback to local cache
    if clean_email in cache:
        cached_entry = cache[clean_email]
        cached_entry["source"] = "offline_cache"
        return cached_entry

    return None


def fetch_leaderboard_from_cloud_or_cache() -> List[Dict[str, Any]]:
    """
    Retrieves global/friends leaderboard ranked by total_score:
    1. Queries Supabase when online.
    2. Falls back to cached friends + current user when offline.
    """
    cfg = get_cloud_config()
    cache = load_friends_cache()

    if cfg["is_configured"] and check_internet_connection():
        if cfg.get("postgres_url"):
            try:
                rows = fetch_leaderboard_via_postgres(cfg["postgres_url"])
                for r in rows:
                    cache[r["email"]] = r
                save_friends_cache(cache)
                return rows
            except Exception as e:
                print(f"[sync_service] Error fetching leaderboard via postgres: {e}")

        if cfg.get("has_rest_key") and cfg.get("supabase_url"):
            try:
                supabase_url = cfg["supabase_url"]
                headers = get_supabase_headers(cfg)

                with httpx.Client(timeout=3.5) as client:
                    url = f"{supabase_url}/rest/v1/ddcet_user_stats?select=*&order=total_score.desc&limit=25"
                    resp = client.get(url, headers=headers)
                    if resp.status_code == 200:
                        rows = resp.json()
                        for r in rows:
                            cache[r["email"]] = r
                        save_friends_cache(cache)
                        return rows
            except Exception as e:
                print(f"[sync_service] Error fetching leaderboard from Supabase: {e}")

    # Return cached entries sorted by total_score descending
    cached_list = list(cache.values())
    cached_list.sort(key=lambda x: float(x.get("total_score") or 0.0), reverse=True)
    return cached_list
