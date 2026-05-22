#!/usr/bin/env bash
# Deploy from Git Bash / WSL. Password: interactive scp/ssh prompt.
set -euo pipefail
HOST="${DEPLOY_HOST:-192.168.164.33}"
REMOTE="root@${HOST}:/trinity/local/ondemand/3.0/network"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$(cd "$ROOT/../trinityx-ood/network" && pwd)"

cd "$ROOT"
npm run build

echo "=== Backend ==="
scp "$BACKEND"/{app.py,rest.py,passenger_wsgi.py,requirements.txt,constant.py,log.py,manifest.yml,Passengerfile.json} "$REMOTE/"

echo "=== Templates ==="
scp "$BACKEND/app/index.html" "$BACKEND/app/error.html" "$REMOTE/app/"

echo "=== Frontend ==="
# Do NOT scp dist/* — dist/index.html overwrites Flask app/index.html; dist/logo.png lands in the wrong path.
scp dist/index.js dist/index.css "$REMOTE/app/assets/"
for f in dist/*.woff*; do [ -f "$f" ] && scp "$f" "$REMOTE/app/assets/"; done
[ -d "$BACKEND/app/assets/vendor" ] && scp -r "$BACKEND/app/assets/vendor" "$REMOTE/app/assets/"

echo "=== Remote setup ==="
ssh "root@$HOST" bash -s <<'EOS'
set -e
cd /trinity/local/ondemand/3.0/network
mkdir -p app/assets/icons app/assets/img tmp
[ -d ../node/app/assets/icons ] && cp -a ../node/app/assets/icons/. app/assets/icons/ || true
[ -f ../node/app/assets/img/logo.png ] && cp -a ../node/app/assets/img/logo.png app/assets/img/logo.png || true
# Vite copies public assets to dist root; punAppAssetUrl() expects app/assets/img/logo.png
if [ -f app/assets/logo.png ] && [ ! -f app/assets/img/logo.png ]; then
  cp -a app/assets/logo.png app/assets/img/logo.png
fi
PY=/trinity/local/python/bin/python3
PIP=/trinity/local/python/bin/pip3
$PIP install -r requirements.txt -q || $PIP install -r requirements.txt
$PY -c "from app import app; print('PYTHON_IMPORT_OK')"
grep -oE 'trinity_node|/api/v1/networks' app/assets/index.js | sort -u | head -5
touch tmp/restart.txt
H="Host: yixin3-dev-ctrl001:8080"
B="https://127.0.0.1:8080/pun/sys/trinity_network"
for p in / /app/assets/index.js /api/v1/networks; do
  echo "HTTP $(curl -sk -o /dev/null -w '%{http_code}' -H "$H" "$B$p") $p"
done
EOS

echo "Done: https://yixin3-dev-ctrl001:8080/pun/sys/trinity_network"
