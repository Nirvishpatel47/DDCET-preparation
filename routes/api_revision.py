from typing import Optional
from fastapi import APIRouter, Query
from services.revision_service import get_due_revisions, get_mistake_patterns

router = APIRouter(prefix="/api/revision", tags=["Revision"])


@router.get("/due")
def list_due_revisions(
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Returns items due for spaced revision."""
    items = get_due_revisions(subject_id=subject_id, topic_id=topic_id, limit=limit)
    return {"due_count": len(items), "questions": items}


@router.get("/mistakes")
def list_mistake_patterns():
    """Returns recurring mistake category distribution."""
    patterns = get_mistake_patterns()
    return {"mistake_patterns": patterns}
