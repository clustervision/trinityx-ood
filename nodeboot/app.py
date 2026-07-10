#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2023  ClusterVision Solutions b.v.
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
Node Boot — OOD GUI for lconsole / node provisioning.

Live view of nodes booting: one card per OS image, progress bars for each group of
nodes sharing a provisioning state (the collapsed hostlist), plus the network and
provisioning method. Data comes from the Luna2 daemon:
  GET /config/node    -> node -> group / osimage / provision_method / interfaces
  GET /monitor/node   -> per-node live state (populated only while provisioning)
"""

__author__      = 'Dev-team'
__copyright__   = 'Copyright 2025, TrinityX[NODEBOOT]'
__license__     = 'GPL'
__version__     = '1.0'
__maintainer__  = 'Dev-team'
__email__       = 'support@clustervision.com'
__status__      = 'Development'

import os
import re
from collections import defaultdict
from configparser import RawConfigParser

import requests
from flask import Flask, render_template, jsonify

from constant import INI_FILE, TOKEN_FILE

requests.packages.urllib3.disable_warnings()

app = Flask(__name__, static_folder="static", template_folder="templates")

# Ordered provisioning pipeline -> progress %. Raw Luna state strings (see
# daemon monitor node_state[204]) plus the post-install 'booted'. Anything not
# listed (e.g. no monitor entry yet) is treated as idle (0%).
STAGE_PCT = {
    "install.started":    5,
    "install.completed":  15,
    "install.prescript":  25,
    "install.partscript": 38,
    "install.postscript": 50,
    "install.roles":      65,
    "install.image":      80,
    "install.finalizing": 92,
    "install.success":    98,
    "booted":             100,
}


# ---------------------------------------------------------------------------
# Luna API client — read luna.ini, cache a token, refresh once on 401/403.
# ---------------------------------------------------------------------------

class LunaAPI:
    def __init__(self):
        p = RawConfigParser()
        p.read(INI_FILE)
        a = p['API']
        self.base = f"{a['PROTOCOL']}://{a['ENDPOINT']}"
        self.user = a['USERNAME']
        self.password = a['PASSWORD']
        self.verify = str(a.get('VERIFY_CERTIFICATE', 'False')).lower() in ('y', 'yes', 'true')
        self._token = None

    def _token_path_ok(self):
        return isinstance(TOKEN_FILE, str)

    def _load_cached(self):
        if self._token:
            return self._token
        if self._token_path_ok() and os.path.isfile(TOKEN_FILE):
            with open(TOKEN_FILE, encoding='utf-8') as fh:
                self._token = fh.read().strip() or None
        return self._token

    def _new_token(self):
        r = requests.post(f'{self.base}/token', json={'username': self.user, 'password': self.password},
                          timeout=5, verify=self.verify)
        r.raise_for_status()
        self._token = r.json()['token']
        if self._token_path_ok():
            with open(TOKEN_FILE, 'w', encoding='utf-8') as fh:
                fh.write(self._token)
            os.chmod(TOKEN_FILE, 0o600)
        return self._token

    def get(self, path):
        token = self._load_cached() or self._new_token()
        url = f'{self.base}{path}'
        r = requests.get(url, headers={'x-access-tokens': token}, timeout=8, verify=self.verify)
        if r.status_code in (401, 403):
            token = self._new_token()
            r = requests.get(url, headers={'x-access-tokens': token}, timeout=8, verify=self.verify)
        r.raise_for_status()
        return r.json()


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested in demo())
# ---------------------------------------------------------------------------

def stage_of(state):
    """(pct, label, kind) for a raw Luna state string."""
    if not state:
        return 0, 'idle', 'idle'
    if 'error' in state:
        return STAGE_PCT.get(state, 0) or 40, 'error', 'error'
    pct = STAGE_PCT.get(state)
    if pct is None:
        return 0, state, 'other'
    label = 'booted' if state == 'booted' else state.replace('install.', '')
    kind = 'done' if pct >= 100 else 'run'
    return pct, label, kind


_NODE_RE = re.compile(r'^(.*?)(\d+)$')

def collapse_hostlist(names):
    """['node001','node002','node004'] -> 'node[001-002],node004'. Non-numeric names pass through."""
    plain, groups = [], defaultdict(list)
    for n in names:
        m = _NODE_RE.match(n)
        if m:
            groups[(m.group(1), len(m.group(2)))].append(int(m.group(2)))
        else:
            plain.append(n)
    out = []
    for (prefix, width), nums in sorted(groups.items()):
        nums.sort()
        start = prev = nums[0]
        for num in nums[1:] + [None]:
            if num == prev + 1:
                prev = num
                continue
            if start == prev:
                out.append(f'{prefix}{start:0{width}d}')
            else:
                out.append(f'{prefix}[{start:0{width}d}-{prev:0{width}d}]')
            start = prev = num
    return ','.join(out + sorted(plain))


def build_sessions(nodes, states):
    """nodes: {name: cfg}, states: {name: raw_state} -> list of session dicts.

    Session = OS image. Racks = nodes bucketed by current state (collapsed hostlist),
    sorted most-advanced first. Same JSON shape the template/JS already consume.
    """
    by_image = defaultdict(list)
    for name, cfg in nodes.items():
        by_image[cfg.get('osimage') or 'unknown'].append(name)

    sessions = []
    for image, members in sorted(by_image.items()):
        sample = nodes[members[0]]
        buckets = defaultdict(list)   # state -> [names]
        pcts = []
        for name in members:
            state = states.get(name)
            pct, _, _ = stage_of(state)
            buckets[state].append(name)
            pcts.append(pct)
        racks = []
        for state, bnames in buckets.items():
            pct, label, kind = stage_of(state)
            racks.append({'name': collapse_hostlist(bnames), 'pct': pct,
                          'stage': label, 'kind': kind, 'count': len(bnames)})
        racks.sort(key=lambda r: (-r['pct'], r['name']))
        overall = round(sum(pcts) / len(pcts)) if pcts else 0
        sessions.append({
            'id': re.sub(r'[^A-Za-z0-9_-]', '-', image),
            'image': image,
            'nodes': collapse_hostlist(members),
            'network': _provision_network(sample),
            'boot': sample.get('provision_method') or 'pxe',
            'overall': overall,
            'racks': racks,
        })
    # Most active sessions first (not fully booted), then by name.
    sessions.sort(key=lambda s: (s['overall'] >= 100, s['image']))
    return sessions


def _provision_network(cfg):
    want = (cfg.get('provision_interface') or 'BOOTIF').upper()
    for iface in cfg.get('interfaces', []):
        if iface.get('interface', '').upper() == want:
            return iface.get('network') or want
    return want


# ---------------------------------------------------------------------------
# Status assembly
# ---------------------------------------------------------------------------

def get_status():
    api = LunaAPI()
    node_data = api.get('/config/node')
    nodes = node_data.get('config', {}).get('node', {}) or {}

    states = {}
    try:
        mon = api.get('/monitor/node')
        entries = mon.get('monitor', {}).get('status', {}).get('node', {}) or {}
        for name, info in entries.items():
            # bulk state is "<name> <raw-state>", e.g. "node001 install.image"
            raw = (info.get('state') or '').strip()
            if raw.startswith(name + ' '):
                raw = raw[len(name) + 1:]
            states[name] = raw or None
    except requests.HTTPError:
        pass  # 404 "no entries found" -> nothing provisioning right now

    return build_sessions(nodes, states)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html", table='Node Boot')


@app.route('/api/status', methods=['GET'])
def status():
    try:
        return jsonify({"sessions": get_status()})
    except Exception as exc:  # surface API/config errors in the UI, don't 500
        app.logger.warning("status failed: %s", exc)
        return jsonify({"sessions": [], "error": str(exc)}), 200


if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.run(host='0.0.0.0', port=7756, debug=True)


def demo():
    # ponytail: one runnable check for the pure logic (no network needed)
    assert stage_of(None) == (0, 'idle', 'idle')
    assert stage_of('booted') == (100, 'booted', 'done')
    assert stage_of('install.image')[0] == 80
    assert stage_of('install.error')[2] == 'error'
    assert collapse_hostlist(['node001', 'node002', 'node003', 'node005']) == 'node[001-003],node005'
    assert collapse_hostlist(['gpu01']) == 'gpu01'
    assert collapse_hostlist(['login', 'node010', 'node011']) == 'node[010-011],login'

    nodes = {
        'node001': {'osimage': 'img', 'provision_method': 'torrent',
                    'provision_interface': 'BOOTIF',
                    'interfaces': [{'interface': 'BOOTIF', 'network': 'cluster'}]},
        'node002': {'osimage': 'img', 'provision_method': 'torrent',
                    'provision_interface': 'BOOTIF',
                    'interfaces': [{'interface': 'BOOTIF', 'network': 'cluster'}]},
    }
    sess = build_sessions(nodes, {'node001': 'booted', 'node002': 'install.roles'})
    assert len(sess) == 1
    s = sess[0]
    assert s['network'] == 'cluster' and s['boot'] == 'torrent'
    assert s['overall'] == round((100 + 65) / 2), s['overall']
    assert [r['stage'] for r in s['racks']] == ['booted', 'roles'], s['racks']
    print("OK: nodeboot logic (stage map, hostlist collapse, session build)")
