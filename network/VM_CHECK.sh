#!/usr/bin/env bash
# Run on the controller as root (or the OOD app user) after deploy.
set -euo pipefail
APP=/trinity/local/ondemand/3.0/network
PY=/trinity/local/python/bin/python3
OOD_HOST="${OOD_HOST:-yixin3-dev-ctrl001}"

echo "=== OOD symlink ==="
ls -la /var/www/ood/apps/sys/trinity_network 2>/dev/null || echo "symlink missing?"

echo "=== Python ==="
ls -la "$PY" "$APP/Passengerfile.json"
"$PY" -c "from app import app; print('IMPORT_OK')"

echo "=== Key files ==="
ls -la "$APP/app/index.html" "$APP/app/assets/index.js" "$APP/ood_wsgi_fix.py"

echo "=== HTTP (on controller) ==="
H="Host: ${OOD_HOST}:8080"
B="https://127.0.0.1:8080/pun/sys/trinity_network"
for p in / /app/assets/index.js /app/assets/index.css /api/v1/networks; do
  code=$(curl -sk -o /dev/null -w '%{http_code}' -H "$H" "$B$p")
  echo "HTTP $code $p"
done

echo "=== Passenger log hint ==="
echo "If still 500: tail -50 /var/log/ondemand-nginx/*/error.log"
