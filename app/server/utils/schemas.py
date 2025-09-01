from pydantic import BaseModel, Field
from typing import Dict, Optional

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
