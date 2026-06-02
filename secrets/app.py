#!/usr/bin/env python3
import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from constant import APP_STATE, INI_FILE, LICENSE, TOKEN_FILE
from log import Log
from rest import Rest

LOGGER = Log.init_log("INFO")
TABLE = "secrets"
API_VERSION = "v1"
ENTITIES = {"group", "node"}

app = Flask(__name__, static_folder="static", template_folder="app")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


@app.before_request
def validate_home_directory():
    if request.path.startswith("/static/"):
        return None
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table="Secrets", data="", error=TOKEN_FILE["error"])
    if not os.path.isfile(INI_FILE):
        return render_template("error.html", table="Secrets", data="", error=f"Luna Configuration File: <strong>{INI_FILE}</strong> Not Found")
    if not os.access(INI_FILE, os.R_OK):
        return render_template("error.html", table="Secrets", data="", error=f"Luna Configuration File: <strong>{INI_FILE}</strong> is not readable.")
    return None


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", table="Secrets", data="", error=f"ERROR :: {e}"), 200


def _response_from_requests(resp, ok_statuses):
    if resp is False or resp is None:
        return {"status": False, "status_code": 500, "content": {"message": "Daemon request failed"}}
    try:
        body = resp.json()
    except Exception:
        body = {"message": resp.text if getattr(resp, "text", "") else "Invalid daemon response"}
    status_ok = resp.status_code in ok_statuses
    return {"status": status_ok, "status_code": resp.status_code, "content": body if isinstance(body, dict) else {"message": str(body)}}


def _secret_payload(entity, owner, secret, path, content):
    return {"config": {TABLE: {entity: {owner: [{"name": secret, "path": path, "content": content}]}}}}


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", APP_URL=request.base_url.rstrip("/"))


@app.route(f"/api/{API_VERSION}/routes", methods=["GET"])
def routes():
    response = []
    for rule in app.url_map.iter_rules():
        if str(rule.endpoint) == "static":
            continue
        method = ",".join(sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"}))
        response.append({"route": f"https://{request.environ['HTTP_HOST']}{rule}", "function": str(rule.endpoint), "method": method})
    return jsonify(response), 200


@app.route(f"/api/{API_VERSION}/secrets", methods=["GET"])
def list_secrets():
    """
    Return all secrets from the Luna daemon.

    Important: always respond with HTTP 200 so the SPA can rely on the
    JSON envelope (`status` + `status_code`) instead of the HTTP code,
    matching the behaviour of the Network / Group / Node backends.
    """
    response = Rest().get_data(TABLE)
    if not response:
        return jsonify(
            {
                "status": False,
                "status_code": 400,
                "content": {"message": "Failed to load secrets from daemon."},
            }
        ), 200
    return jsonify({"status": True, "status_code": 200, "content": response}), 200


@app.route(f"/api/{API_VERSION}/add", methods=["POST"])
def add_secret():
    payload = request.get_json(silent=True) or {}
    entity = str(payload.get("entity", "")).strip().lower()
    owner = str(payload.get("owner", "")).strip()
    secret = str(payload.get("secret", "")).strip()
    path = str(payload.get("path", "")).strip()
    content = str(payload.get("content", ""))
    if entity not in ENTITIES or not owner or not secret:
        return jsonify({"status": False, "status_code": 400, "content": {"message": "entity, owner and secret are required"}}), 400
    request_data = _secret_payload(entity, owner, secret, path, content)
    resp = Rest().post_data(TABLE, f"{entity}/{owner}", request_data)
    return jsonify(_response_from_requests(resp, {201, 204})), 200


@app.route(f"/api/{API_VERSION}/update", methods=["PUT"])
def update_secret():
    payload = request.get_json(silent=True) or {}
    original = payload.get("original", {})
    updated = payload.get("updated", {})
    entity = str(original.get("entity", "")).strip().lower()
    owner = str(original.get("owner", "")).strip()
    secret = str(original.get("secret", "")).strip()
    new_name = str(updated.get("secret", secret)).strip()
    path = str(updated.get("path", "")).strip()
    content = str(updated.get("content", ""))
    if entity not in ENTITIES or not owner or not secret:
        return jsonify({"status": False, "status_code": 400, "content": {"message": "original.entity, original.owner and original.secret are required"}}), 400
    request_data = _secret_payload(entity, owner, new_name, path, content)
    resp = Rest().post_data(TABLE, f"{entity}/{owner}/{secret}", request_data)
    return jsonify(_response_from_requests(resp, {204, 201})), 200


@app.route(f"/api/{API_VERSION}/clone", methods=["POST"])
def clone_secret():
    payload = request.get_json(silent=True) or {}
    original = payload.get("original", {})
    clone = payload.get("clone", {})
    entity = str(original.get("entity", "")).strip().lower()
    owner = str(original.get("owner", "")).strip()
    secret = str(original.get("secret", "")).strip()
    new_name = str(clone.get("secret", "")).strip()
    path = str(clone.get("path", "")).strip()
    content = str(clone.get("content", ""))
    if entity not in ENTITIES or not owner or not secret or not new_name:
        return jsonify({"status": False, "status_code": 400, "content": {"message": "original + clone.secret are required"}}), 400
    request_data = _secret_payload(entity, owner, secret, path, content)
    request_data["config"][TABLE][entity][owner][0]["newsecretname"] = new_name
    resp = Rest().post_clone(TABLE, f"{entity}/{owner}/{secret}", request_data)
    return jsonify(_response_from_requests(resp, {201, 204})), 200


@app.route(f"/api/{API_VERSION}/delete/<string:entity>/<string:owner>/<string:secret>", methods=["DELETE"])
def delete_secret(entity, owner, secret):
    if entity not in ENTITIES:
        return jsonify({"status": False, "status_code": 400, "content": {"message": "entity must be group or node"}}), 400
    resp = Rest().get_delete(TABLE, f"{entity}/{owner}/{secret}")
    return jsonify(_response_from_requests(resp, {204})), 200


@app.route(f"/api/{API_VERSION}/license", methods=["GET"])
def license_info():
    response = "LICENSE Information is not available at this moment."
    if os.path.isfile(LICENSE) and os.access(LICENSE, os.R_OK):
        with open(LICENSE, "r", encoding="utf-8") as file_data:
            response = "<br />".join(file_data.readlines())
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7755, debug=(APP_STATE is False))
