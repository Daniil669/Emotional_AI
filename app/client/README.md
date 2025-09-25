# Emotion AI Client (React Native + Expo)

Mobile UI for **text & audio emotion recognition** with feedback and lightweight analytics.

- Built with **Expo** (React Native)
- Screens for **Home**, **Text**, **Audio**, and **Analytics**
- Works with the FastAPI backend (see `server/` README)
- Simple config file to point the app at your API

---

## Project Structure

```
client/
└─ my-app/
   ├─ src/
   │  ├─ components/
   │  │  ├─ ButtonPrimary.js
   │  │  ├─ FeedbackModal.js
   │  │  ├─ ProbabilityList.js
   │  │  ├─ StarRating.js
   │  │  └─ StatCard.js
   │  ├─ navigation/
   │  │  └─ index.js                # stack / tabs
   │  ├─ screens/
   │  │  ├─ AnalyticsScreen.js
   │  │  ├─ AudioScreen.js
   │  │  ├─ HomeScreen.js
   │  │  └─ TextScreen.js
   │  ├─ theme/
   │  │  └─ colors.js
   │  └─ utils/
   │     ├─ api.js                  # fetch helpers
   │     └─ config.js               # API base & client settings
   ├─ .gitignore
   ├─ App.js
   ├─ app.json
   ├─ babel.config.js
   ├─ config.example.txt            # example of config values
   ├─ package.json
   └─ package-lock.json
```

---

## Prerequisites

- Node.js 18+
- Expo CLI (`npx expo` comes with `expo` via `npm i -g expo-cli` or just use `npx`)
- A running backend (see `/server`)
- For **AudioScreen** on a device/emulator: microphone permission enabled

---

## Quickstart

```bash
cd client/my-app

# 1) Install dependencies
npm install
# or: yarn

# 2) Configure API base
# Edit src/utils/config.js and set API_BASE to your backend URL
# (e.g., http://localhost:8000 for local emulator)
# A sample of expected values is in config.example.txt

# 3) Run the app
npx expo start              # opens Metro bundler
# Press 'a' for Android, 'i' for iOS, or scan QR with Expo Go
# If your device is not on the same network, you can try:
# npx expo start --tunnel
```

> **Note:** When running on a physical phone, `http://localhost` refers to the **phone**, not your computer. Use your computer's LAN IP or set up a tunnel. Avoid embedding private IPs in the repo; use `config.js` to change it locally.

---

## Configuration (`src/utils/config.js`)

Minimal example:

```js
// src/utils/config.js
export const API_BASE = "http://localhost:8000"; // or your LAN IP / tunneled URL
export const TIMEOUT_MS = 15000;
```

`api.js` uses `API_BASE` for all requests:
- `POST /api/text/predict`
- `POST /api/audio/predict` (multipart with `file`)
- `POST /api/feedback`
- `GET  /api/analytics/*`

---

## Features

- **Home**: simple entry + quick links.
- **TextScreen**: enter text, get multi-label probabilities, send feedback (1–5 ⭐ + optional comment).
- **AudioScreen**: record/stop/send audio to backend; shows predicted label(s); send feedback.
- **AnalyticsScreen**: calls backend analytics endpoints (stars distribution, summary, etc.).
- **Feedback modal**: appears after a prediction so users can rate the result.

---

## Typical Flows

### Text
1. Type a sentence and submit.
2. See top probabilities in `ProbabilityList`.
3. Tap **Rate** → choose stars + optional comment → **Submit**.

### Audio
1. Tap **Record** → speak → **Stop**.
2. Send the clip to the API (formats handled by Expo Audio/FileSystem).
3. Rate the result in the same modal flow.

---

## Troubleshooting

- **Device can’t reach API**  
  - Use `npx expo start --tunnel`, or replace `API_BASE` with your computer’s LAN IP (e.g., `http://192.168.x.x:8000`).  
  - Confirm CORS is enabled on the backend for the Expo origin (see server README).

- **Microphone permission error on AudioScreen**  
  - Ensure the permission hook/request is called before recording.  
  - In Expo Go, grant mic permission in device settings.

- **Metro bundler cache issues**  
  - `npx expo start -c` to clear cache.

- **Duplicate imports / naming collisions**  
  - If bundling fails with “Identifier has already been declared,” check `utils/api.js` or other files for duplicate imports/definitions.

---

## Scripts

Common scripts via `npm`:
```jsonc
{
  "scripts": {
    "start": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios",
    "web": "expo start --web",
    "lint": "eslint ."
  }
}
```

> `run:android` / `run:ios` require native project prebuild; otherwise use Expo Go with `expo start`.

---
