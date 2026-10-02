#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2026  ClusterVision Solutions b.v.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

"""
Development mode for the TrinityX OOD apps.

An app runs this when its constant.py has APP_STATE = False and it is started with
`python app.py`. It starts the app's Vite dev server next to Flask, and the page Flask
renders loads the live frontend from Vite instead of the built app/assets/index.js,
so frontend and backend changes both reload without a build.

Passenger imports app.py and never runs it as __main__, so none of this is reachable in
production, and this file is not part of the package.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2026, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '3.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import atexit
import hashlib
import logging
import os
import re
import signal
import socket
import subprocess
import sys
import time
from flask import Flask, redirect, request
from werkzeug.exceptions import NotFound

VITE_PORT = 5173
VITE_START_TIMEOUT = 120
NODE_MODULES_CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'trinityx-ood-dev')
LOCK_STAMP = '.trinityx-ood-dev-lock'
# The frontends call /<app>-backend/... in dev mode; their Vite proxy used to strip it.
BACKEND_PREFIX = re.compile(r'^/[A-Za-z0-9_]+-backend(?=/|$)')
ENTRY_SCRIPT = re.compile(r'<script\s+type="module"\s+src="([^"]+)"')

LOGGER = logging.getLogger('trinityx-ood-dev')
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False
_console = logging.StreamHandler(sys.stderr)
_console.setFormatter(logging.Formatter('[dev] %(message)s'))
LOGGER.addHandler(_console)


def run_dev(app: Flask, port: int) -> None:
    """
    Start Vite for the app's frontend/ folder, then run Flask in debug mode on the given port.
    """
    frontend = os.path.join(app.root_path, 'frontend')
    entries = _entry_scripts(frontend)
    # Flask's reloader runs this module twice: a watcher parent and the serving child,
    # marked by Werkzeug with WERKZEUG_RUN_MAIN. Vite belongs to the parent, which outlives the restarts.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        _start_vite(frontend, os.path.basename(app.root_path))
        LOGGER.info('Open http://<this-host>:%s/ - the page loads the live frontend from port %s.', port, VITE_PORT)
    _serve_live_frontend(app, entries)
    app.run(host='0.0.0.0', port=port, debug=True)


def _entry_scripts(frontend: str) -> list[str]:
    """
    Read the module entry points (e.g. /src/main.ts) from the frontend's own index.html.
    """
    index = os.path.join(frontend, 'index.html')
    if not os.path.isfile(index):
        raise SystemExit(f'ERROR :: {index} not found, there is no frontend to run for this app.')
    with open(index, 'r', encoding='utf-8') as html:
        entries = ENTRY_SCRIPT.findall(html.read())
    if not entries:
        raise SystemExit(f'ERROR :: No <script type="module" src="..."> entry found in {index}.')
    return entries


def _start_vite(frontend: str, name: str) -> None:
    """
    Install node_modules when the lock file changed, start Vite and stop it on exit.
    """
    on_fuse = _mount_type(frontend).startswith('fuse')
    node_modules = os.path.join(frontend, 'node_modules')
    if on_fuse:
        _mount_local_node_modules(node_modules, name)
    _install_node_modules(frontend, node_modules)
    command = [os.path.join(node_modules, '.bin', 'vite'),
               '--host', '0.0.0.0', '--port', str(VITE_PORT), '--strictPort', '--cors']
    # A FUSE mount raises no file events for edits made on the other side, so Vite has to poll.
    env = dict(os.environ, CHOKIDAR_USEPOLLING='true') if on_fuse else None
    vite = subprocess.Popen(command, cwd=frontend, env=env, start_new_session=True)
    atexit.register(_stop, vite)
    signal.signal(signal.SIGHUP, lambda *_: sys.exit(0))
    _wait_for_port(vite)


def _mount_type(path: str) -> str:
    """
    Return the filesystem type of the mount that holds path.
    """
    path = os.path.realpath(path)
    best, fstype = '', ''
    with open('/proc/self/mounts', 'r', encoding='utf-8') as mounts:
        for line in mounts:
            fields = line.split()
            point = fields[1].replace('\\040', ' ')
            inside = path == point or path.startswith(point.rstrip('/') + '/')
            if inside and len(point) > len(best):
                best, fstype = point, fields[2]
    return fstype


def _mount_local_node_modules(node_modules: str, name: str) -> None:
    """
    Bind-mount a node_modules on local disk over the one in a FUSE-mounted checkout.
    Such mounts often cannot hold symlinks, and their node_modules may be built for another OS.
    """
    if os.geteuid() != 0:
        raise SystemExit('ERROR :: Run as root: the checkout is on a FUSE mount and its '
                         'node_modules has to be bind-mounted from local disk.')
    local = os.path.join(NODE_MODULES_CACHE, name, 'node_modules')
    os.makedirs(local, exist_ok=True)
    os.makedirs(node_modules, exist_ok=True)
    if not os.path.ismount(node_modules):
        subprocess.run(['mount', '--bind', local, node_modules], check=True)
    atexit.register(subprocess.run, ['umount', node_modules], check=False)
    LOGGER.info('node_modules: %s is mounted from %s', node_modules, local)


def _install_node_modules(frontend: str, node_modules: str) -> None:
    """
    Run npm ci when package-lock.json differs from the one node_modules was installed from.
    """
    with open(os.path.join(frontend, 'package-lock.json'), 'rb') as lock:
        digest = hashlib.sha256(lock.read()).hexdigest()
    stamp = os.path.join(node_modules, LOCK_STAMP)
    if os.path.isfile(stamp):
        with open(stamp, 'r', encoding='utf-8') as installed:
            if installed.read() == digest:
                return
    LOGGER.info('package-lock.json changed, running npm ci in %s', frontend)
    subprocess.run(['npm', 'ci'], cwd=frontend, check=True)
    with open(stamp, 'w', encoding='utf-8') as installed:
        installed.write(digest)


def _wait_for_port(vite: subprocess.Popen) -> None:
    """
    Wait until Vite accepts connections, failing if it exits or does not come up.
    """
    deadline = time.monotonic() + VITE_START_TIMEOUT
    while time.monotonic() < deadline:
        if vite.poll() is not None:
            raise SystemExit(f'ERROR :: Vite exited with code {vite.returncode}.')
        try:
            socket.create_connection(('127.0.0.1', VITE_PORT), timeout=1).close()
            return
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f'ERROR :: Vite did not listen on port {VITE_PORT} within {VITE_START_TIMEOUT} seconds.')


def _stop(vite: subprocess.Popen) -> None:
    """
    Stop Vite and everything it started.
    """
    if vite.poll() is not None:
        return
    os.killpg(vite.pid, signal.SIGTERM)
    try:
        vite.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(vite.pid, signal.SIGKILL)


def _vite_origin() -> str:
    """
    Vite's origin on the address the browser used to reach Flask.
    Vite only accepts IP addresses and localhost as a host, so a hostname is not used.
    """
    address = request.environ['werkzeug.socket'].getsockname()[0]
    if ':' in address:
        address = f'[{address}]'
    return f'http://{address}:{VITE_PORT}'


def _serve_live_frontend(app: Flask, entries: list[str]) -> None:
    """
    Point the page Flask renders at Vite, and send unknown asset requests there too.
    """
    static = re.escape(app.static_url_path)
    built_script = re.compile(rf'<script\b[^>]*\bsrc="{static}/index\.js[^"]*"[^>]*>\s*</script>')
    built_style = re.compile(rf'<link\b[^>]*\bhref="{static}/index\.css[^"]*"[^>]*>')
    app_not_found = app.error_handler_spec[None][404].get(NotFound)

    def live_frontend(response):
        if response.mimetype != 'text/html' or response.direct_passthrough:
            return response
        html = response.get_data(as_text=True)
        if not built_script.search(html):
            return response
        origin = _vite_origin()
        tags = '\n'.join(f'<script type="module" src="{origin}{src}"></script>'
                         for src in ['/@vite/client', *entries])
        response.set_data(built_script.sub(lambda _: tags, built_style.sub('', html), count=1))
        return response

    def not_found(error):
        wants_json = (request.accept_mimetypes.best == 'application/json'
                      or request.headers.get('X-Requested-With') == 'XMLHttpRequest')
        if request.method != 'GET' or wants_json:
            return app_not_found(error) if app_not_found else error
        path = request.full_path.rstrip('?')
        if path.startswith(f'{app.static_url_path}/'):
            path = path[len(app.static_url_path):]
        return redirect(f'{_vite_origin()}{path}', code=307)

    app.wsgi_app = _StripBackendPrefix(app.wsgi_app)
    app.after_request(live_frontend)
    app.register_error_handler(404, not_found)


class _StripBackendPrefix:
    """
    WSGI middleware that removes a leading /<app>-backend from the request path.
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        environ['PATH_INFO'] = BACKEND_PREFIX.sub('', environ.get('PATH_INFO', ''), count=1) or '/'
        return self.wsgi_app(environ, start_response)
