from fastapi import APIRouter
from services.analytics_service import get_dashboard_analytics
from services.adaptive_service import calculate_adaptive_priorities

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def dashboard_metrics():
    """Provides complete dashboard metrics, daily recommendations, and progress tracking."""
    return get_dashboard_analytics()


@router.get("/adaptive-priorities")
def adaptive_priorities():
    """Returns rule-based topic priority scores with component breakdowns and explanations."""
    priorities = calculate_adaptive_priorities()
    return {"priorities": priorities}
