from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import date

# Requests
class TextRequest(BaseModel):
    text: str = Field(min_length=1)
    lang: Optional[str] = Field(default=None, min_length=2, max_length=8)

class FeedbackRequest(BaseModel):
    prediction_id: str = Field(min_length=8)
    stars: int = Field(ge=0, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)

# Responses 
class PredictionInputInfo(BaseModel):
    text_len: Optional[int] = None
    lang: Optional[str] = None
    duration_sec: Optional[float] = None
    sample_rate: Optional[int] = None

class PredictionResponse(BaseModel):
    prediction_id: str
    top_label: str
    confidence: float
    scores: Dict[str, float]
    model_name: str
    model_version: str
    processing_ms: int
    input: PredictionInputInfo

class AudioPredictionResponse(PredictionResponse):
    pass

class FeedbackResponse(BaseModel):
    ok: bool
    feedback_id: int

# Errors 
class ErrorEnvelope(BaseModel):
    error: dict | None = None

# Analytics
class AccuracyByFeedback(BaseModel):
    correct: int
    incorrect: int
    denominator: int
    accuracy: Optional[float] = None

class ModalitySummary(BaseModel):
    modality: str
    total: int
    with_feedback: int
    feedback_rate: float
    avg_confidence: Optional[float] = None
    high_conf_share: Optional[float] = None
    avg_stars: Optional[float] = None
    stars_distribution: Dict[str, int]
    avg_processing_ms: Optional[float] = None
    accuracy_by_feedback: AccuracyByFeedback

class EmotionBucketExt(BaseModel):
    label: str
    count: int
    avg_confidence: Optional[float] = None
    avg_stars: Optional[float] = None
    accuracy_by_feedback: AccuracyByFeedback

class TimeseriesPoint(BaseModel):
    day: date | str
    count: int

class DuplicatesSummary(BaseModel):
    groups: int
    with_label_disagreement: int
    disagreement_rate: Optional[float] = None

class LanguageStat(BaseModel):
    lang: str
    count: int

class AudioSummary(BaseModel):
    avg_duration_sec: Optional[float] = None
    avg_sample_rate: Optional[float] = None

class Comparison(BaseModel):
    accuracy_delta: Optional[float] = None
    avg_confidence_delta: Optional[float] = None
    feedback_rate_delta: Optional[float] = None
    avg_processing_ms_delta: Optional[float] = None
    high_conf_share_delta: Optional[float] = None
    avg_stars_delta: Optional[float] = None

class AnalyticsResponse(BaseModel):
    window_days: Optional[int] = None
    modality_filter: Optional[str] = None
    thresholds: dict
    totals_by_modality: dict
    overall: dict
    modality_summaries: Dict[str, ModalitySummary]
    comparison: Optional[Comparison] = None
    by_emotion: List[EmotionBucketExt]
    timeseries: List[TimeseriesPoint]
    duplicates: DuplicatesSummary
    language_stats: List[LanguageStat]
    audio_stats: AudioSummary


