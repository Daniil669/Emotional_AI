from fastapi import APIRouter, Depends
from sqlalchemy import text as sqltext
from sqlalchemy.orm import Session
from utils.db import get_db
from utils.model_adapters import get_text_meta, get_audio_meta, MODE as ADAPTER_MODE

router = APIRouter()

@router.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    try:
        db.execute(sqltext("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    counts = {"predictions": 0, "feedback": 0}
    try:
        counts["predictions"] = db.execute(sqltext("SELECT COUNT(*) FROM predictions")).scalar()
        counts["feedback"]    = db.execute(sqltext("SELECT COUNT(*) FROM feedback")).scalar()
    except Exception:
        pass

    return {
        "status": "ok" if db_ok else "degraded",
        "db_ok": db_ok,
        "mode_env": ADAPTER_MODE,
        "counts": counts,
        "models": {"text": get_text_meta(), "audio": get_audio_meta()},
    }
