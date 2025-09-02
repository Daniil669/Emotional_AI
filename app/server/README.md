# Emotion AI Backend (FastAPI + SQLite)

Prototype API for text & audio emotion predictions with user feedback.
- Clean separation: **routes ↔ adapters ↔ data models**
- SQLite storage with two tables: `predictions` and `feedback`
- Deterministic **mock** models so you can test right away

## Quickstart
```bash
cd server
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
