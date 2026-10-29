from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from services.auth_service import get_current_user, login_user, update_profile
from services.stats_service import compute_comprehensive_stats
from services.supabase_sync_service import sync_current_user_stats

router = APIRouter(prefix="/api/auth", tags=["Auth & Profile"])


class LoginRequest(BaseModel):
    email: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    display_name: str
    avatar: str


@router.get("/current")
def get_user_profile():
    """Returns current active local user."""
    return {"user": get_current_user()}


@router.post("/login")
def login(req: LoginRequest):
    """
    Sets local active user session and attempts cloud sync.
    Works 100% offline; if offline, enqueues profile and stats locally.
    """
    try:
        user = login_user(req.email, req.display_name, req.avatar)
        # Compute latest stats for this user and queue/push to cloud
        stats = compute_comprehensive_stats()
        sync_result = sync_current_user_stats(stats)
        return {
            "success": True,
            "user": user,
            "sync": sync_result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {e}")


@router.post("/profile")
def update_user_profile(req: ProfileUpdateRequest):
    """Updates display name and avatar for current user."""
    updated = update_profile(req.display_name, req.avatar)
    stats = compute_comprehensive_stats()
    sync_result = sync_current_user_stats(stats)
    return {
        "success": True,
        "user": updated,
        "sync": sync_result
    }
