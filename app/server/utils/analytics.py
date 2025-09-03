from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from utils.models import Prediction, Feedback

def _apply_common_filters(q, cutoff_dt, modality):
    conds = []
    if cutoff_dt is not None:
        conds.append(Prediction.created_at >= cutoff_dt)
    if modality in ("text", "audio"):
        conds.append(Prediction.modality == modality)
    if conds:
        q = q.filter(*conds)
    return q

def _stars_dist(db: Session, cutoff_dt, modality) -> Dict[str, int]:
    q = (
        db.query(Feedback.stars, func.count(Feedback.id))
          .join(Prediction, Feedback.prediction_id == Prediction.prediction_id)
    )
    q = _apply_common_filters(q, cutoff_dt, modality)
    rows = q.group_by(Feedback.stars).all()
    dist = {str(k): 0 for k in range(1, 6)}
    for s, c in rows:
        if s in (1,2,3,4,5):
            dist[str(s)] = int(c or 0)
    return dist

def _with_feedback_count(db: Session, cutoff_dt, modality) -> int:
    sub = (
        db.query(Feedback.prediction_id.label("pid"))
          .join(Prediction, Feedback.prediction_id == Prediction.prediction_id)
    )
    sub = _apply_common_filters(sub, cutoff_dt, modality)
    return sub.distinct().count()

def _accuracy_by_feedback(db: Session, cutoff_dt, modality, correct_gte: int, incorrect_lte: int):
    q = (
        db.query(
            func.sum(case((Feedback.stars >= correct_gte, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.stars <= incorrect_lte, 1), else_=0)).label("incorrect"),
        )
        .join(Prediction, Feedback.prediction_id == Prediction.prediction_id)
    )
    q = _apply_common_filters(q, cutoff_dt, modality)
    row = q.one()
    correct = int(row.correct or 0)
    incorrect = int(row.incorrect or 0)
    denom = correct + incorrect
    acc = (correct / denom) if denom else None
    return {"correct": correct, "incorrect": incorrect, "denominator": denom, "accuracy": acc}

def _modality_summary(
    db: Session,
    cutoff_dt,
    modality: str,
    high_conf_thr: float,
    correct_gte: int,
    incorrect_lte: int,
):
    # totals
    base = _apply_common_filters(db.query(Prediction), cutoff_dt, modality)
    total = base.count()
    with_fb = _with_feedback_count(db, cutoff_dt, modality)
    fb_rate = (with_fb / total) if total else 0.0

    # confidence stats
    avg_conf = base.with_entities(func.avg(Prediction.confidence)).scalar()
    high_conf = (
        _apply_common_filters(db.query(Prediction), cutoff_dt, modality)
            .filter(Prediction.confidence >= high_conf_thr)
            .count()
    )
    high_conf_share = (high_conf / total) if total else None

    # avg stars
    avg_stars = (
        _apply_common_filters(
            db.query(func.avg(Feedback.stars)),
            cutoff_dt,
            modality
        )
        .join(Prediction, Feedback.prediction_id == Prediction.prediction_id)
        .scalar()
    )

    # processing time
    avg_proc = base.with_entities(func.avg(Prediction.processing_ms)).scalar()

    # distributions and accuracy
    stars_dist = _stars_dist(db, cutoff_dt, modality)
    acc = _accuracy_by_feedback(db, cutoff_dt, modality, correct_gte, incorrect_lte)

    return {
        "modality": modality,
        "total": total,
        "with_feedback": with_fb,
        "feedback_rate": fb_rate,
        "avg_confidence": float(avg_conf) if avg_conf is not None else None,
        "high_conf_share": float(high_conf_share) if high_conf_share is not None else None,
        "avg_stars": float(avg_stars) if avg_stars is not None else None,
        "stars_distribution": stars_dist,
        "avg_processing_ms": float(avg_proc) if avg_proc is not None else None,
        "accuracy_by_feedback": acc,
    }

def _per_emotion_breakdown(
    db: Session, cutoff_dt, modality, correct_gte: int, incorrect_lte: int
) -> List[Dict[str, Any]]:
    q = (
        db.query(
            Prediction.top_label.label("label"),
            func.count(Prediction.id).label("count"),
            func.avg(Prediction.confidence).label("avg_conf"),
            func.avg(Feedback.stars).label("avg_stars"),
            func.sum(case((Feedback.stars >= correct_gte, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.stars <= incorrect_lte, 1), else_=0)).label("incorrect"),
        )
        .outerjoin(Feedback, Feedback.prediction_id == Prediction.prediction_id)
    )
    q = _apply_common_filters(q, cutoff_dt, modality)
    rows = q.group_by(Prediction.top_label).order_by(func.count(Prediction.id).desc()).all()

    out = []
    for r in rows:
        correct = int(r.correct or 0)
        incorrect = int(r.incorrect or 0)
        denom = correct + incorrect
        acc = (correct / denom) if denom else None
        out.append({
            "label": r.label,
            "count": int(r.count or 0),
            "avg_confidence": float(r.avg_conf) if r.avg_conf is not None else None,
            "avg_stars": float(r.avg_stars) if r.avg_stars is not None else None,
            "accuracy_by_feedback": {
                "correct": correct, "incorrect": incorrect,
                "denominator": denom, "accuracy": acc
            }
        })
    return out

def _timeseries(db: Session, cutoff_dt, modality):
    day_col = func.date(Prediction.created_at).label("day")
    q = _apply_common_filters(
        db.query(day_col, func.count(Prediction.id).label("count")),
        cutoff_dt, modality
    )
    rows = q.group_by(day_col).order_by(day_col.asc()).all()
    return [{"day": r.day, "count": int(r.count or 0)} for r in rows]

def _duplicates_summary(db: Session, cutoff_dt, modality):
    sub = (
        _apply_common_filters(
            db.query(
                Prediction.input_hash.label("ih"),
                func.count(Prediction.id).label("n"),
                func.count(distinct(Prediction.top_label)).label("labels"),
            ),
            cutoff_dt, modality
        )
        .group_by(Prediction.input_hash)
        .having(func.count(Prediction.id) > 1)
        .subquery()
    )
    # total duplicate groups
    total_groups = db.query(func.count()).select_from(sub).scalar() or 0
    # groups where labels disagree
    disagree = db.query(func.count()).select_from(sub).filter(sub.c.labels > 1).scalar() or 0
    rate = (disagree / total_groups) if total_groups else None
    return {"groups": int(total_groups), "with_label_disagreement": int(disagree), "disagreement_rate": rate}

def _language_stats(db: Session, cutoff_dt):
    q = _apply_common_filters(
        db.query(Prediction.lang, func.count(Prediction.id)),
        cutoff_dt, "text"
    )
    rows = q.group_by(Prediction.lang).order_by(func.count(Prediction.id).desc()).all()
    return [{"lang": (r[0] or "und"), "count": int(r[1] or 0)} for r in rows]

def _audio_summary(db: Session, cutoff_dt):
    q = _apply_common_filters(
        db.query(func.avg(Prediction.duration_sec), func.avg(Prediction.sample_rate)),
        cutoff_dt, "audio"
    )
    avg_dur, avg_sr = q.one()
    return {
        "avg_duration_sec": float(avg_dur) if avg_dur is not None else None,
        "avg_sample_rate": float(avg_sr) if avg_sr is not None else None,
    }

def compute_analytics(
    db: Session,
    since_days: Optional[int] = 30,
    modality: Optional[str] = None,
    *,
    correct_gte: int = 4,
    incorrect_lte: int = 2,
    high_conf_thr: float = 0.80,
) -> Dict[str, Any]:
    """
    Returns a comprehensive analytics dict.
    accuracy by feedback treats stars >= correct_gte as Correct,
    stars <= incorrect_lte as Incorrect, and 3-star (or missing) as Neutral/ignored.
    """
    cutoff_dt = datetime.utcnow() - timedelta(days=since_days) if since_days else None

    # Global totals by modality (for headers and quick cards)
    totals_by_modality = {
        m: _apply_common_filters(db.query(Prediction), cutoff_dt, m).count()
        for m in ("text", "audio")
    }

    # Per-modality summaries
    summaries = {}
    for m in ("text", "audio"):
        if modality and m != modality:
            continue
        summaries[m] = _modality_summary(
            db, cutoff_dt, m, high_conf_thr, correct_gte, incorrect_lte
        )

    # Comparison (text and audio)
    comparison = None
    if ("text" in summaries) and ("audio" in summaries):
        def _delta(key):
            a = summaries["audio"].get(key)
            t = summaries["text"].get(key)
            if a is None or t is None: return None
            return float(a - t)
        def _acc(m):
            acc = summaries[m]["accuracy_by_feedback"]["accuracy"]
            return acc if acc is not None else None

        comparison = {
            "accuracy_delta": ( (_acc("audio") - _acc("text")) if (_acc("audio") is not None and _acc("text") is not None) else None ),
            "avg_confidence_delta": _delta("avg_confidence"),
            "feedback_rate_delta": _delta("feedback_rate"),
            "avg_processing_ms_delta": _delta("avg_processing_ms"),
            "high_conf_share_delta": _delta("high_conf_share"),
            "avg_stars_delta": _delta("avg_stars"),
        }

    # Emotion breakdown (filtered by modality if provided)
    by_emotion = _per_emotion_breakdown(db, cutoff_dt, modality, correct_gte, incorrect_lte)

    # Timeseries (filtered by modality if provided)
    timeseries = _timeseries(db, cutoff_dt, modality)

    # Duplicates consistency (based on input_hash)
    duplicates = _duplicates_summary(db, cutoff_dt, modality)

    # Text language mix and audio recording stats
    language_stats = _language_stats(db, cutoff_dt)
    audio_stats    = _audio_summary(db, cutoff_dt)

    # Feedback coverage overall
    with_fb_overall = _with_feedback_count(db, cutoff_dt, modality)
    total_overall   = _apply_common_filters(db.query(Prediction), cutoff_dt, modality).count()

    return {
        "window_days": since_days,
        "modality_filter": modality,
        "thresholds": {
            "correct_gte": correct_gte,
            "incorrect_lte": incorrect_lte,
            "high_confidence": high_conf_thr,
        },
        "totals_by_modality": totals_by_modality,
        "overall": {
            "total_predictions": total_overall,
            "total_with_feedback": with_fb_overall,
            "feedback_rate": (with_fb_overall / total_overall) if total_overall else 0.0,
        },
        "modality_summaries": summaries,# { "text": {...}, "audio": {...} }
        "comparison": comparison,# deltas audio - text
        "by_emotion": by_emotion,# per label, with accuracy_by_feedback
        "timeseries": timeseries, # [{day, count}]
        "duplicates": duplicates, # stability on repeated inputs
        "language_stats": language_stats,# for text
        "audio_stats": audio_stats,# for audio
    }
