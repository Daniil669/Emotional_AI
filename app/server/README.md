# Emotion AI Backend (FastAPI + SQLite)

Prototype API for **text & audio emotion predictions** with user feedback and analytics.

- Clean separation: **routes ↔ adapters ↔ data models**
- SQLite storage (`data/app.db`) with two core tables: `predictions` and `feedback`
- Ready to serve a React Native (Expo) client via simple CORS config

---

## Project Structure

```
server/
├─ data/
│  └─ app.db                      # SQLite database (auto-created)
├─ routes/
│  ├─ __init__.py
│  ├─ analytics.py                # /api/analytics/* endpoints
│  ├─ audio.py                    # /api/audio/* endpoints
│  ├─ feedback.py                 # /api/feedback endpoint
│  ├─ health.py                   # /api/healthz
│  └─ text.py                     # /api/text/* endpoints
├─ utils/
│  ├─ __init__.py
│  ├─ analytics.py                # server-side analytics helpers
│  ├─ audio_utils.py              # audio helpers (e.g., waveform/loader)
│  ├─ db.py                       # SQLAlchemy engine/session + init
│  ├─ id.py                       # id generation helpers
│  ├─ model_adapters.py           # mock/real model wrappers
│  ├─ models.py                   # SQLAlchemy ORM models
│  ├─ schemas.py                  # Pydantic request/response models
│  └─ timing.py                   # timing decorators / utilities
├─ .env                           # local configuration (not committed)
├─ .env.example                   # sample env you can copy
├─ main.py                        # FastAPI app factory & router includes
├─ requirements.txt
└─ README.md
```

> Tip: exact paths and endpoint names are visible in the files under `routes/`. The names below match the current structure but always check those files for the source of truth.

---

## Quickstart

Requirements: Python 3.10+ recommended.

```bash
cd server

# 1) Create and activate a virtual env
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3) (Optional) Configure environment
# Copy defaults and tweak if needed
cp .env.example .env   # on Windows: copy .env.example .env

# 4) Run the API (dev)
uvicorn main:app --reload --port 8000
```

---

## Environment (.env)

A minimal setup typically works out-of-the-box. Use `.env` only if you want to override defaults.

Common keys you might see in this project:

```
# Allow the Expo dev client or web app in development
CORS_ALLOW_ORIGINS=http://localhost:19006,http://localhost:5173

# Optional model locations or flags (if using real models instead of mocks)
# MODE= MOCK or REAL
# TEXT_MODEL_DIR=
# TEXT_LABELS_PATH=

# AUDIO_MODEL_DIR=
# AUDIO_LABELS_PATH=
```

If unsure, start without changes. Add keys gradually as you enable real models.

---

## API Overview

Base path: `/api`

### Health
- `GET /api/healthz` → returns `{"status":"ok"}`

### Text
- `POST /api/text/predict`
  - JSON: `{ "text": "I am thrilled with the result!" }`
  - Returns prediction scores and a `prediction_id` you can later reference in feedback.

### Audio
- `POST /api/audio/predict`
  - `multipart/form-data` with:
    - `file=@sample.wav`
    - (optionally) `sample_rate=16000`
  - Returns prediction and a `prediction_id`.

### Feedback
- `POST /api/feedback`
  - JSON: `{ "prediction_id": "<uuid>", "stars": 1..5, "comment": "optional" }`
  - Stored in `feedback` table.

### Analytics
- Typical endpoints exposed under `/api/analytics/*` (exact routes in `routes/analytics.py`), e.g.:
  - `/api/analytics/summary`
  - `/api/analytics/stars`
  - `/api/analytics/accuracy`
  - These aggregate the `predictions` & `feedback` tables to provide quick insights.

> **Note:** Endpoint names above mirror the code layout. If you changed route prefixes locally, refer to the files under `routes/` for the current paths.

---

## Example Requests

Health:
```bash
curl http://localhost:8000/api/healthz
```

Text prediction:
```bash
curl -X POST http://localhost:8000/api/text/predict   -H "Content-Type: application/json"   -d '{"text":"I am excited to start!"}'
```

Audio prediction:
```bash
curl -X POST "http://localhost:8000/api/audio/predict"   -F "file=@path/to/sample.wav"   -F "sample_rate=16000"
```

Send feedback (link it to a prior prediction):
```bash
curl -X POST http://localhost:8000/api/feedback   -H "Content-Type: application/json"   -d '{"prediction_id":"<your-id>","stars":5,"comment":"Great!"}'
```

---

## Development Notes

- **Database reset**: stop the server and delete `server/data/app.db` to start fresh.
- **Mock vs real models**: the `utils/model_adapters.py` can load deterministic mocks by default; you can later point it to real models via environment variables or by editing the adapter.
- **CORS**: If your mobile/web client can’t reach the API, confirm allowed origins in your FastAPI CORS config and your `.env` (e.g., Expo runs at `http://localhost:19006`).

---

