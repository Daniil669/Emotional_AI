# Emotional_AI

---

## Emotion Recognition from Voice and Text Using AI

A bachelor’s thesis project that builds a **mobile application** to recognize emotions from either **written text** or **spoken audio**.  
It consists of two specialized models (BERT for text, SpeechBrain for audio), a **FastAPI** backend that serves predictions and collects **feedback** in SQLite, and an **Expo/React Native** client for real-world, on-device testing. The project also includes reproducible training notebooks and exported evaluation artifacts for transparent comparison between modalities.

---

## Project Structure

```
ai/   # AI model training, notebooks, scripts, exported checkpoints & evaluation
app/  # General readme for the mobile client and backend (how to run both)
client/  # Expo (React Native) mobile app source
server/  # FastAPI backend with SQLite (predictions + feedback + analytics)
```

---

## Related READMEs

- **AI assets & results:** `ai/README.md` — models, labels, metrics, notebooks, how to plug models into the backend.
- **App umbrella:** `app/README.md` — quickstart for running client + server together; notes for mixed OS/WSL setups.
- **Client (Expo):** `client/README.md` — app structure, config (`API_BASE`), and troubleshooting.
- **Server (FastAPI):** `server/README.md` — endpoints, env, database, and mock vs real models.

> Start at the **app README** for the fastest end‑to‑end run, then dive into the **client** and **server** READMEs as needed.

---

## Deliverables

- A mobile app that detects emotions from user-provided **voice** or **text**
- Two AI models: **BERT** for text, **SpeechBrain** for voice
- **SQLite** feedback system to track and compare predictions
- Accuracy and **comparative analysis** report between voice and text models

---

## Technologies

| Layer     | Tools/Frameworks            |
|---------- |-----------------------------|
| Frontend  | React Native (Expo)         |
| Backend   | FastAPI                     |
| Text AI   | BERT, GoEmotions            |
| Voice AI  | SpeechBrain, RAVDESS        |
| Storage   | SQLite (local)              |

---

## Getting Started

Clone this repository and follow setup instructions inside the **`/ai`**, **`/app`**, **`/client`**, and **`/server`** folders.  
For development on a phone, configure the client’s `API_BASE` (see `client/src/utils/config.js`) to reach your backend URL.

---

## Thesis Info

- **Author:** Daniil Shchennikov  
- **Supervisor:** Johan Dams  
- **Institution:** VAMK University of Applied Sciences
