from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, JSON, ForeignKey, Text, Index
from sqlalchemy.sql import func
from utils.db import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prediction_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    modality: Mapped[str] = mapped_column(String(10))# "text"  "audio"

    # text metadata
    text_len: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lang: Mapped[str | None] = mapped_column(String(8), nullable=True)

    # audio metadata
    duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # model info
    model_name: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(32))

    # outputs
    top_label: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    scores: Mapped[dict] = mapped_column(JSON)

    processing_ms: Mapped[int] = mapped_column(Integer)

    # privacy: store only hash of raw input (text or audio bytes)
    input_hash: Mapped[str] = mapped_column(String(64), index=True)

Index("ix_predictions_modality_created", Prediction.modality, Prediction.created_at)

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prediction_id: Mapped[str] = mapped_column(String(36), ForeignKey("predictions.prediction_id", ondelete="CASCADE"))
    submitted_at: Mapped[str] = mapped_column(server_default=func.now())
    stars: Mapped[int] = mapped_column(Integer)  # 0..5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
