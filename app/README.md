# Emotion AI App (Client + Server)

This folder ties together the **FastAPI backend** and the **Expo (React Native) client** used in the Emotion AI thesis project.

- **server/** – FastAPI + SQLite API for text & audio predictions, feedback, and analytics.
- **client/** – Expo mobile UI (Text, Audio, Analytics screens) that talks to the API.

For detailed usage, see each subfolder’s README.

---

## Quickstart (Dev)

### 1) Backend
```bash
cd server
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Swagger docs: <http://localhost:8000/docs>

### 2) Client
```bash
cd client/my-app
npm install
# Set API base URL in src/utils/config.js (e.g., http://localhost:8000)
npx expo start
# press 'a' for Android, 'i' for iOS, or use the QR code with Expo Go
```

> **Tip:** If your phone can’t reach `localhost`, use your computer’s LAN IP or `npx expo start --tunnel`.

---

## WSL / Mixed-OS Networking Note

If your **backend runs inside WSL** and you want to reach it from a **phone** connected to your Windows hotspot/LAN, you may need to **port forward** from Windows to WSL. One common approach is using **netsh portproxy** on Windows to forward a public Windows port to the WSL IP and to allow it through the Windows Firewall. I used it:)

High-level steps (PowerShell, placeholders only — don’t paste literally):
```
$WindowsIP = "<your-windows-lan-ip>"
$WSLIP     = "<your-wsl-ip>"
$Port      = 8000

# Forward Windows:<Port> → WSL:<Port>
netsh interface portproxy add v4tov4 listenaddress=$WindowsIP listenport=$Port connectaddress=$WSLIP connectport=$Port

# Allow the port in Windows Firewall (restrict to your hotspot/subnet if needed)
netsh advfirewall firewall add rule name="WSL $Port (hotspot only)" dir=in action=allow protocol=TCP localport=$Port remoteip=<your-subnet-cidr>
```

To **inspect / remove** later:
```
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=$WindowsIP listenport=$Port
netsh advfirewall firewall delete rule name="WSL 8000 (hotspot only)"
```

> Most users running everything on **one machine** (Windows/macOS/Linux) won’t need this; set `API_BASE` to `http://localhost:8000` or your LAN IP and run the client with `expo start`.

---

## Environments & Config

- **Backend**: optional `.env` at `server/.env` (see `server/.env.example`).
- **Client**: set `API_BASE` in `client/my-app/src/utils/config.js`.

---

