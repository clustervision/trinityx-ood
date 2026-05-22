# Deploy TrinityX Network OOD app (run from Documents\network after npm run build)
# Usage: .\scripts\deploy.ps1
# You will be prompted for root@192.168.164.33 password.

$ErrorActionPreference = "Stop"
$HostAddr = "192.168.164.33"
$Remote = "root@${HostAddr}:/trinity/local/ondemand/3.0/network"
$Backend = "..\trinityx-ood\network"
$Dist = ".\dist"

if (-not (Test-Path "$Dist\index.js")) {
    Write-Host "Run: npm run build" -ForegroundColor Red
    exit 1
}

Write-Host "=== 1) Backend Python ===" -ForegroundColor Cyan
scp "$Backend\app.py" "$Backend\rest.py" "$Backend\passenger_wsgi.py" "$Backend\requirements.txt" `
    "$Backend\constant.py" "$Backend\log.py" "$Backend\ood_wsgi_fix.py" "$Backend\manifest.yml" `
    "$Backend\Passengerfile.json" "${Remote}/"

Write-Host "=== 2) Flask templates (NOT dist/index.html) ===" -ForegroundColor Cyan
scp "$Backend\app\index.html" "$Backend\app\error.html" "${Remote}/app/"

Write-Host "=== 3) Frontend bundle ONLY (index.js + index.css + fonts) ===" -ForegroundColor Cyan
scp "$Dist\index.js" "$Dist\index.css" "${Remote}/app/assets/"
Get-ChildItem "$Dist\*.woff*" -ErrorAction SilentlyContinue | ForEach-Object {
    scp $_.FullName "${Remote}/app/assets/"
}

if (Test-Path "$Backend\app\assets\vendor") {
    Write-Host "=== 4) Vendor fonts ===" -ForegroundColor Cyan
    scp -r "$Backend\app\assets\vendor" "${Remote}/app/assets/"
}

Write-Host "=== 5) Remote setup + restart ===" -ForegroundColor Cyan
$RemoteCmd = @'
set -e
cd /trinity/local/ondemand/3.0/network
mkdir -p app/assets/icons app/assets/img tmp
[ -d ../node/app/assets/icons ] && cp -a ../node/app/assets/icons/. app/assets/icons/ || true
[ -f ../node/app/assets/img/logo.png ] && cp -a ../node/app/assets/img/logo.png app/assets/img/ || true
PY=/trinity/local/python/bin/python3
PIP=/trinity/local/python/bin/pip3
$PIP install -r requirements.txt -q || $PIP install -r requirements.txt
$PY -c "from app import app; print('PYTHON_IMPORT_OK')"
echo "--- bundle ---"
grep -oE 'trinity_node|trinity_network|/api/v1/networks' app/assets/index.js | sort -u | head -5
ls -la app/assets/index.js
touch tmp/restart.txt
BASE="https://127.0.0.1:8080/pun/sys/trinity_network"
H="Host: yixin3-dev-ctrl001:8080"
for p in "/" "/app/assets/index.js" "/api/v1/networks"; do
  c=$(curl -sk -o /dev/null -w "%{http_code}" -H "$H" "$BASE$p")
  echo "HTTP $c $p"
done
'@
ssh "root@$HostAddr" $RemoteCmd

Write-Host "Done. Open: https://yixin3-dev-ctrl001:8080/pun/sys/trinity_network" -ForegroundColor Green
