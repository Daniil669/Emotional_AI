from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from routes.text import router as text_router
from routes.audio import router as audio_router
from routes.feedback import router as feedback_router
from routes.analytics import router as analytics_router
from routes.health import router as health_router
from utils.db import Base, engine

# Ensure data folder exists (for SQLite file)
Path("data").mkdir(parents=True, exist_ok=True)

# Create tables on startup (simple prototype)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Emotion AI Backend", version="0.1.0")

# CORS: loosen for prototype
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set to RN dev URL & prod domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefix everything with /api (no versioning per decision)
app.include_router(health_router, prefix="/api")
app.include_router(text_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
