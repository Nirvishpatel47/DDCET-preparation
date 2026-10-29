from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from config import get_cloud_config
from services.supabase_sync_service import (
    load_sync_queue,
    sync_pending_queue,
    sync_current_user_stats,
    check_internet_connection
)
from services.stats_service import compute_comprehensive_stats

router = APIRouter(prefix="/api/sync", tags=["Cloud Sync"])


@router.get("/status")
def get_sync_status():
    """
    Returns current network connectivity, Supabase configuration status,
    and number of pending items in local sync queue.
    """
    cfg = get_cloud_config()
    queue = load_sync_queue()
    is_online = check_internet_connection()

    return {
        "online": is_online,
        "is_configured": cfg["is_configured"],
        "supabase_url": cfg["supabase_url"] if cfg["is_configured"] else None,
        "pending_count": len(queue),
        "pending_items": [
            {
                "email": item.get("email"),
                "queued_at": item.get("queued_at"),
                "total_questions": item.get("total_questions"),
                "total_score": item.get("total_score")
            }
            for item in queue
        ]
    }


@router.post("/push")
def push_pending_sync():
    """
    Triggers an immediate sync of current user stats and any pending queue items to Supabase.
    If offline, reports that items remain stored locally.
    """
    # 1. Update current stats in queue
    current_stats = compute_comprehensive_stats()
    direct_res = sync_current_user_stats(current_stats)

    # 2. Flush queue
    flush_res = sync_pending_queue()

    return {
        "success": direct_res.get("synced", False) or flush_res.get("status") == "success",
        "direct_sync": direct_res,
        "queue_sync": flush_res,
        "online": check_internet_connection()
    }
