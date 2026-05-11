# -*- coding: utf-8 -*-
"""
OOD (nginx + Phusion Passenger) sometimes passes PATH_INFO that still contains the Pun
mount prefix (e.g. /pun/sys/<app>/app/assets/...). Flask's static route is only
registered for /app/assets/..., so the request misses → 404 → if your error handler
returns HTML with HTTP 200, the browser shows a broken <img> (Content-Type: text/html).

This is not specific to Group vs Node — both apps use static_url_path="/app/assets".
If Passenger gives a clean PATH_INFO, you never see the bug; if not, you need this fix.

Usage (right after Flask(...) creation, before CORS if any):

    from ood_wsgi_fix import apply_ood_path_fix
    apply_ood_path_fix(app)
"""


def apply_ood_path_fix(app):
    """Wrap app.wsgi_app so PATH_INFO is normalized for /app/assets/... requests."""
    app.wsgi_app = _FixOODMountPathInfo(app.wsgi_app)
    return app


class _FixOODMountPathInfo(object):
    __slots__ = ("_app",)

    def __init__(self, app):
        self._app = app

    @staticmethod
    def _normalize_path(path, script):
        path = path or "/"
        script = (script or "").rstrip("/")
        changed = False

        if script:
            if path == script:
                path = "/"
                changed = True
            elif path.startswith(script + "/"):
                path = path[len(script):] or "/"
                changed = True

        marker = "/app/assets/"
        if not path.startswith(marker):
            idx = path.find(marker)
            if idx != -1:
                path = path[idx:]
                changed = True

        if path and not path.startswith("/"):
            path = "/" + path.lstrip("/")
            changed = True

        return path, changed

    def __call__(self, environ, start_response):
        path, changed = self._normalize_path(
            environ.get("PATH_INFO") or "/",
            environ.get("SCRIPT_NAME") or "",
        )
        if changed:
            environ = environ.copy()
            environ["PATH_INFO"] = path
        return self._app(environ, start_response)
