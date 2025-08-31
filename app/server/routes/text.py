from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from utils.db import get_db
from utils.schemas import TextRequest, PredictionResponse, ErrorEnvelope
from utils.model_adapters import predict_text, get_text_meta
from utils.models import Prediction
from utils.id import new_uuid, sha256_of
from utils.timing import timed_ms

router = APIRouter()

MAX_TEXT_LEN = 512

@router.post("/text", response_model=PredictionResponse, responses={422: {"model": ErrorEnvelope}})
def post_text(req: TextRequest, db: Session = Depends(get_db)):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail={"code": "EMPTY_TEXT", "message": "Provide non-empty text."})
    if len(text) > MAX_TEXT_LEN:
        raise HTTPException(status_code=413, detail={"code": "TEXT_TOO_LONG", "message": f"Max {MAX_TEXT_LEN} chars."})

    with timed_ms() as t:
        scores = predict_text(text=text, lang=req.lang)
    processing_ms = t.ms

    # derive top label/conf
    top_label = max(scores, key=scores.get)
    confidence = float(scores[top_label])

    pid = new_uuid()
    meta = get_text_meta()
    rec = Prediction(
        prediction_id=pid,
        modality="text",
        text_len=len(text),
        lang=req.lang or "und",
        duration_sec=None,
        sample_rate=None,
        model_name=meta["name"],
        model_version=meta["version"],
        top_label=top_label,
        confidence=confidence,
        scores=scores,
        processing_ms=processing_ms,
        input_hash=sha256_of(text),
    )
    db.add(rec)
    db.commit()

    return {
        "prediction_id": pid,
        "top_label": top_label,
        "confidence": confidence,
        "scores": scores,
        "model_name": meta["name"],
        "model_version": meta["version"],
        "processing_ms": processing_ms,
        "input": {"text_len": len(text), "lang": rec.lang},
    }
