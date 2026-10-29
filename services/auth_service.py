import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from config import CURRENT_USER_FILE


DEFAULT_USER = {
    "email": "cadet@ddcet.local",
    "display_name": "DDCET Cadet",
    "avatar": "⚡",
    "created_at": datetime.utcnow().isoformat(),
    "is_guest": True
}


def get_current_user() -> Dict[str, Any]:
    """Retrieves current local active user from current_user.json."""
    if os.path.isfile(CURRENT_USER_FILE):
        try:
            with open(CURRENT_USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("email"):
                    return data
        except Exception as e:
            print(f"[auth_service] Error reading current user: {e}")
    
    # Save and return default
    save_current_user(DEFAULT_USER)
    return DEFAULT_USER


def save_current_user(user_data: Dict[str, Any]):
    """Persists current user locally."""
    try:
        with open(CURRENT_USER_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)
    except Exception as e:
        print(f"[auth_service] Error saving current user: {e}")


def login_user(email: str, display_name: Optional[str] = None, avatar: Optional[str] = None) -> Dict[str, Any]:
    """
    Logs in or registers a user locally.
    Normalized email is the unique identifier across local and cloud stats.
    """
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise ValueError("Please provide a valid email address.")

    current = get_current_user()
    
    # Derive display name if not provided
    name = display_name.strip() if display_name and display_name.strip() else None
    if not name:
        if current.get("email") == clean_email and current.get("display_name"):
            name = current["display_name"]
        else:
            name = clean_email.split("@")[0].capitalize()

    ava = avatar.strip() if avatar and avatar.strip() else current.get("avatar", "⚡")

    user_data = {
        "email": clean_email,
        "display_name": name,
        "avatar": ava,
        "created_at": current.get("created_at") if current.get("email") == clean_email else datetime.utcnow().isoformat(),
        "is_guest": False,
        "last_login": datetime.utcnow().isoformat()
    }

    save_current_user(user_data)
    return user_data


def update_profile(display_name: str, avatar: str) -> Dict[str, Any]:
    """Updates display name and avatar for current active user."""
    current = get_current_user()
    if display_name and display_name.strip():
        current["display_name"] = display_name.strip()
    if avatar and avatar.strip():
        current["avatar"] = avatar.strip()
    current["updated_at"] = datetime.utcnow().isoformat()
    save_current_user(current)
    return current
