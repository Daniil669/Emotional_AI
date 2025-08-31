from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from utils.db import get_db
from utils.schemas import FeedbackRequest, FeedbackResponse, ErrorEnvelope
from utils.models import Prediction, Feedback

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse, responses={404: {"model": ErrorEnvelope}})
def post_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    # Ensure prediction exists
    pred = db.scalar(select(Prediction).where(Prediction.prediction_id == req.prediction_id))
    if not pred:
        raise HTTPException(status_code=404, detail={"code": "PREDICTION_NOT_FOUND", "message": "Unknown prediction_id."})

    fb = Feedback(prediction_id=req.prediction_id, stars=req.stars, comment=req.comment)
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return {"ok": True, "feedback_id": fb.id}
