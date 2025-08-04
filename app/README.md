# Application – Mobile App + Backend

This folder contains the code for the **user-facing application**, split into:

- `client/`: React Native mobile app
- `server/`: FastAPI backend for serving AI predictions

---

## Tech Stack

| Layer       | Tools            |
|-------------|------------------|
| Mobile App  | React Native     |
| Backend API | FastAPI          |
| Storage     | SQLite (for feedback) |

---

## Features

- Users can input **text** or **record voice**
- The app sends input to FastAPI backend
- The backend returns the predicted emotion
- Feedback/corrections are stored locally via SQLite

---

## Structure

app/
├── client/ # React Native source code
└── server/ # FastAPI endpoints and model wrappers

---

## 📦 Setup Instructions

### Backend (FastAPI)
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

### Mobile App (React Native)
```bash
cd client
npm install
npx react-native run-android
```