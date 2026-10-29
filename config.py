import os
import json
import base64
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_PATH = os.path.join(BASE_DIR, ".env")
ENV_EXAMPLE_PATH = os.path.join(BASE_DIR, ".env.example")

os.makedirs(DATA_DIR, exist_ok=True)

SYNC_QUEUE_FILE = os.path.join(DATA_DIR, "sync_queue.json")
CURRENT_USER_FILE = os.path.join(DATA_DIR, "current_user.json")
FRIENDS_CACHE_FILE = os.path.join(DATA_DIR, "friends_cache.json")


def load_env_file() -> Dict[str, str]:
    """Loads environment variables from .env if present without requiring external libraries."""
    env_vars: Dict[str, str] = {}
    if os.path.isfile(ENV_PATH):
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        env_vars[k] = v
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            print(f"[config] Error reading .env file: {e}")
    return env_vars


# Initial load
_loaded_env = load_env_file()


def derive_supabase_url_from_jwt(api_key: str) -> Optional[str]:
    """If api_key is a Supabase JWT (starts with eyJ...), extract the project ref to build the URL."""
    if not api_key or not isinstance(api_key, str) or not api_key.startswith("eyJ"):
        return None
    try:
        parts = api_key.split(".")
        if len(parts) >= 2:
            payload_b64 = parts[1]
            padded = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
            decoded = json.loads(base64.b64decode(padded.encode("ascii")).decode("utf-8", errors="ignore"))
            ref = decoded.get("ref")
            if ref and isinstance(ref, str):
                return f"https://{ref}.supabase.co"
    except Exception:
        pass
    return None


def get_cloud_config() -> Dict[str, Any]:
    """Returns the current Cloud / Supabase configuration."""
    # Reload .env if updated at runtime
    if os.path.isfile(ENV_PATH):
        load_env_file()

    raw_db_api_key = os.environ.get("DATABASE_API_KEY", "").strip()
    raw_supabase_key = (
        os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
        or os.environ.get("SUPABASE_SERVICE_KEY")
        or ""
    ).strip()

    # Determine PostgreSQL database URL
    postgres_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or ""
    ).strip()

    # If DATABASE_API_KEY was populated with a postgres:// connection string
    if raw_db_api_key.startswith("postgresql://") or raw_db_api_key.startswith("postgres://"):
        if not postgres_url:
            postgres_url = raw_db_api_key
        # Since raw_db_api_key is a postgres URL, the REST key is only valid if raw_supabase_key exists
        rest_api_key = raw_supabase_key
    else:
        rest_api_key = raw_supabase_key or raw_db_api_key

    supabase_url = (
        os.environ.get("SUPABASE_URL")
        or os.environ.get("DATABASE_URL_SUPABASE")
        or ""
    ).strip()

    # Derive Supabase URL from postgres connection string if omitted
    if not supabase_url and postgres_url:
        import re
        match = re.search(r"@(?:db\.)?([a-z0-9]+)\.supabase\.", postgres_url)
        if match:
            supabase_url = f"https://{match.group(1)}.supabase.co"
        else:
            pooler_match = re.search(r"postgres\.([a-z0-9]+):", postgres_url)
            if pooler_match:
                supabase_url = f"https://{pooler_match.group(1)}.supabase.co"

    # Derive URL from JWT if not explicitly set
    if not supabase_url and rest_api_key:
        derived = derive_supabase_url_from_jwt(rest_api_key)
        if derived:
            supabase_url = derived

    # Clean URL trailing slash
    if supabase_url.endswith("/"):
        supabase_url = supabase_url[:-1]

    has_rest_key = bool(rest_api_key and not (rest_api_key.startswith("postgresql://") or rest_api_key.startswith("postgres://")))
    is_postgres = bool(postgres_url)
    is_configured = bool(has_rest_key or is_postgres)

    return {
        "api_key": rest_api_key,
        "postgres_url": postgres_url,
        "supabase_url": supabase_url,
        "has_rest_key": has_rest_key,
        "is_postgres": is_postgres,
        "is_configured": is_configured,
        "env_path": ENV_PATH,
        "sync_queue_file": SYNC_QUEUE_FILE,
        "current_user_file": CURRENT_USER_FILE,
        "friends_cache_file": FRIENDS_CACHE_FILE
    }
