# routes/analytics.py
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from utils.db import get_db
from utils.analytics import compute_analytics
from utils.schemas import AnalyticsResponse

router = APIRouter()

@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Aggregate + compare text vs audio using feedback-derived accuracy"
)
def get_analytics(
    days: int = Query(30, ge=0, le=365, description="Look-back window in days (0=all)"),
    modality: Optional[str] = Query(None, pattern="^(text|audio)$", description="Optional filter"),
    correct_gte: int = Query(4, ge=1, le=5, description="Stars ≥ this = Correct"),
    incorrect_lte: int = Query(2, ge=1, le=5, description="Stars ≤ this = Incorrect"),
    high_conf_thr: float = Query(0.80, ge=0.0, le=1.0, description="Confidence threshold for 'high'"),
    db: Session = Depends(get_db),
):
    """
    Accuracy by feedback definition:
      Correct if stars >= correct_gte
      Incorrect if stars <= incorrect_lte
      3-star or missing = Neutral (excluded from denominator)
    """
    return compute_analytics(
        db,
        since_days=(days if days > 0 else None),
        modality=modality,
        correct_gte=correct_gte,
        incorrect_lte=incorrect_lte,
        high_conf_thr=high_conf_thr,
    )
