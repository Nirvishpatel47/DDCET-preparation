from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.stats_service import compute_comprehensive_stats
from services.battle_service import (
    get_all_friends_with_stats,
    add_friend_by_email,
    remove_friend_by_email,
    compare_head_to_head,
    get_battle_leaderboard
)
from services.supabase_sync_service import (
    fetch_friend_stats_from_cloud_or_cache,
    sync_current_user_stats
)

router = APIRouter(prefix="/api/battle", tags=["Battle Arena & Friends"])


class AddFriendRequest(BaseModel):
    friend_email: str


@router.get("/stats")
def get_user_detailed_stats():
    """
    Returns user's comprehensive local stats, including topic-wise MCQs done/not done breakdown.
    Also triggers a background sync update.
    """
    stats = compute_comprehensive_stats()
    # Opportunistic sync
    sync_current_user_stats(stats)
    return {"stats": stats}


@router.get("/friends")
def list_friends():
    """Returns list of tracked competitor friends and their stats."""
    friends = get_all_friends_with_stats()
    return {"friends": friends, "count": len(friends)}


@router.post("/friends")
def add_friend(req: AddFriendRequest):
    """
    Adds a friend by email to track their progress and compete head-to-head.
    Queries Supabase or creates local tracker.
    """
    try:
        res = add_friend_by_email(req.friend_email)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add friend: {e}")


@router.delete("/friends/{friend_email}")
def remove_friend(friend_email: str):
    """Removes a friend from the local competitors list."""
    removed = remove_friend_by_email(friend_email)
    return {"success": removed, "message": f"Removed {friend_email} from competitors."}


@router.get("/compare/{friend_email}")
def get_head_to_head_comparison(friend_email: str):
    """
    Computes side-by-side battle comparison between current user and friend.
    Includes metric duels and topic-by-topic MCQs done/not done comparison matrix.
    """
    try:
        user_stats = compute_comprehensive_stats()
        comparison = compare_head_to_head(user_stats, friend_email)
        return comparison
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {e}")


@router.get("/leaderboard")
def get_leaderboard():
    """Returns full ranked leaderboard of friends and competitors."""
    leaderboard = get_battle_leaderboard()
    return {"leaderboard": leaderboard, "total_competitors": len(leaderboard)}
