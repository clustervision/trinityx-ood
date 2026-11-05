# TrinityX Network Frontend

Vue 3 + TypeScript SPA for the Luna2 Network Open OnDemand app.

## Development

1. Copy `.env.development.example` to `.env.development` and set `VITE_APP_URL` to your Flask network backend (default port `7755`).
2. Install and run:

```bash
npm install
npm run dev
```

Vite serves on port **5173** and proxies `/network-backend` to `VITE_APP_URL`.

## Production build & deploy (OOD)

```bash
npm run build
```

**Only** copy the built bundle into the **network** app assets (not `node`):

```bash
scp dist/index.js dist/index.css root@<controller>:/trinity/local/ondemand/3.0/network/app/assets/
```

Do **not** overwrite `app/index.html` with `dist/index.html`. Flask serves `app/index.html` (Jinja + `APP_URL`); the Vite `dist/index.html` is for local preview only.

Backend (Python) to the app root:

```bash
scp -r trinityx-ood/network/* root@<controller>:/trinity/local/ondemand/3.0/network/
```

On the controller, install Python deps (includes `flask-cors`, required by `app.py`):

```bash
cd /trinity/local/ondemand/3.0/network
pip3 install -r requirements.txt
```

If the app still returns 500, verify import:

```bash
cd /trinity/local/ondemand/3.0/network
/usr/bin/python3.10 -c "from app import app; print('ok')"
```

Check Passenger/OOD logs, e.g. `/var/log/ondemand-nginx/<user>/error.log`.

### Trinity Python on the controller

OOD apps use the Trinity venv, not `/usr/bin/python3.10`:

```bash
source /trinity/local/python/bin/activate
which python3   # → /trinity/local/python/bin/python3
```

`Passengerfile.json` must point at that interpreter:

```json
{ "engine": "builtin", "python": "/trinity/local/python/bin/python3" }
```

Install deps into the **same** venv:

```bash
cd /trinity/local/ondemand/3.0/network
/trinity/local/python/bin/pip3 install -r requirements.txt
/trinity/local/python/bin/python3 -c "from app import app; print('ok')"
touch tmp/restart.txt
```

### One-command deploy (from this machine)

After `npm run build`, run (you will be prompted for the controller password):

```powershell
cd Documents\network
.\scripts\deploy.ps1
```

Or Git Bash: `bash scripts/deploy.sh`

**Do not** run `scp -r network/*` after copying `dist/*` — that restores the old Node bundle and causes 404.

## Backend

API: `trinityx-ood/network` — see `README.md` there for `/api/v1/networks`, `/add`, `/update`, `/rename`, `/delete`, `/nextip`, `/ipinfo`, `/reserve`.
