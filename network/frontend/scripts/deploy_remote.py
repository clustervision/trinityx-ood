#!/usr/bin/env python3
"""Deploy network OOD app to controller and run smoke tests."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import paramiko

HOST = os.environ.get("DEPLOY_HOST", "192.168.164.33")
USER = os.environ.get("DEPLOY_USER", "root")
PASSWORD = os.environ.get("DEPLOY_PASS", "")
REMOTE_ROOT = "/trinity/local/ondemand/3.0/network"
OOD_TEST_HOST = os.environ.get("OOD_HOST", "yixin3-dev-ctrl001")

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT.parent
BACKEND = DOCS / "trinityx-ood" / "network"
DIST = ROOT / "dist"


def sftp_mkdirs(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    parts = remote_dir.strip("/").split("/")
    cur = ""
    for p in parts:
        cur += "/" + p
        try:
            sftp.stat(cur)
        except OSError:
            sftp.mkdir(cur)


def upload_file(sftp: paramiko.SFTPClient, local: Path, remote: str) -> None:
    sftp_mkdirs(sftp, os.path.dirname(remote))
    sftp.put(str(local), remote)
    print(f"  put {local.name} -> {remote}")


def upload_tree(sftp: paramiko.SFTPClient, local_dir: Path, remote_dir: str) -> None:
    for path in local_dir.rglob("*"):
        if path.is_file():
            rel = path.relative_to(local_dir).as_posix()
            upload_file(sftp, path, f"{remote_dir}/{rel}")


def run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    print(f"$ {cmd}")
    _in, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return code, out, err


def main() -> int:
    if not PASSWORD:
        print("Set DEPLOY_PASS environment variable.", file=sys.stderr)
        return 1
    if not BACKEND.is_dir():
        print(f"Missing backend: {BACKEND}", file=sys.stderr)
        return 1
    if not (DIST / "index.js").is_file():
        print("Run npm run build first.", file=sys.stderr)
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {USER}@{HOST}...")
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    sftp = client.open_sftp()

    print("\n=== Upload backend (Python) ===")
    for name in (
        "app.py",
        "rest.py",
        "passenger_wsgi.py",
        "requirements.txt",
        "constant.py",
        "log.py",
        "manifest.yml",
        "Passengerfile.json",
    ):
        upload_file(sftp, BACKEND / name, f"{REMOTE_ROOT}/{name}")

    print("\n=== Upload Flask templates ===")
    upload_file(sftp, BACKEND / "app" / "index.html", f"{REMOTE_ROOT}/app/index.html")
    upload_file(sftp, BACKEND / "app" / "error.html", f"{REMOTE_ROOT}/app/error.html")

    print("\n=== Upload frontend bundle (dist) ===")
    for name in ("index.js", "index.css"):
        upload_file(sftp, DIST / name, f"{REMOTE_ROOT}/app/assets/{name}")
    for woff in DIST.glob("*.woff*"):
        upload_file(sftp, woff, f"{REMOTE_ROOT}/app/assets/{woff.name}")

    vendor = BACKEND / "app" / "assets" / "vendor"
    if vendor.is_dir():
        print("\n=== Upload vendor fonts ===")
        upload_tree(sftp, vendor, f"{REMOTE_ROOT}/app/assets/vendor")

    sftp.close()

    print("\n=== Remote setup ===")
    setup = f"""
set -e
cd {REMOTE_ROOT}
mkdir -p app/assets/icons app/assets/img tmp
if [ -d ../node/app/assets/icons ]; then
  cp -a ../node/app/assets/icons/. app/assets/icons/ 2>/dev/null || true
fi
if [ -f ../node/app/assets/img/logo.png ]; then
  cp -a ../node/app/assets/img/logo.png app/assets/img/logo.png
fi
pip3 install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt
/usr/bin/python3 -c "from app import app; print('PYTHON_IMPORT_OK')"
echo "--- bundle check ---"
grep -oE 'trinity_node|trinity_network|/api/v1/networks' app/assets/index.js | sort -u | head -5
ls -la app/assets/index.js app/index.html
touch tmp/restart.txt 2>/dev/null || true
"""
    code, _, _ = run(client, setup)
    if code != 0:
        print("Remote setup failed.", file=sys.stderr)
        client.close()
        return code

    print("\n=== HTTP smoke tests (on controller) ===")
    tests = f"""
BASE="https://127.0.0.1:8080/pun/sys/trinity_network"
H="Host: {OOD_TEST_HOST}:8080"
for path in "/" "/app/assets/index.js" "/app/assets/index.css" "/api/v1/networks"; do
  code=$(curl -sk -o /dev/null -w '%{{http_code}}' -H "$H" "$BASE$path")
  echo "HTTP $code $path"
done
"""
    run(client, tests)

    client.close()
    print("\nDeploy finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
