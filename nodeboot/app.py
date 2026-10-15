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

Live view of nodes booting: one row per OS image, expandable into its real
Luna groups (node.group — a rack/pool grouping, not a state bucket), each
with booted/booting/failed counts and a 3-phase breakdown of "booting" for
the wave chart (redesign, 30 Jul 2026 — "a few states, not all of them").
Data comes from the Luna2 daemon:
  GET /config/node    -> node -> group / osimage / interfaces
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
import sys
import re
from collections import defaultdict
from configparser import RawConfigParser

import requests
from flask import Flask, render_template, jsonify, abort, url_for, request
from luna.boot import Boot

from constant import (
    INI_FILE, TOKEN_FILE, LICENSE, SOL_GRAB_URL, SOL_GRAB_TIMEOUT, APP_STATE,
)

requests.packages.urllib3.disable_warnings()

app = Flask(__name__, static_folder="app/assets", static_url_path="/app/assets", template_folder="app")

_NODE_NAME_RE = re.compile(r'^[A-Za-z0-9_.-]+$')  # matches STRICT_NAMES-style node names

# The stage tables behind `luna boot status` (luna2-cli 2.2) are the one source of
# truth for the Boot Overview / Boot Progress numbers, so the web view and the CLI
# agree. Boot.__init__ parses CLI arguments, which is why the instance is created
# without it: only the tables and the pure classifiers are used.
_BOOT = Boot.__new__(Boot)

# Ordered provisioning pipeline -> progress %. Raw Luna state strings, straight
# from daemon monitor node_state[204] — 'install.booted' is the post-install
# state reported by the node's own OS at first boot (TRIX-1221), just another
# link in the same chain now. Anything not listed (e.g. no monitor entry yet)
# is treated as idle (0%).
STAGE_PCT = {
    "install.discovered": 4,
    "install.rendered":   8,
    "install.started":    10,
    "install.scripts":    12,
    "install.prescript":  16,
    "install.setupbmc":   22,
    "install.partscript": 28,
    "install.downloaded": 38,
    "install.download":   40,
    "install.completed":  50,
    "install.unpack":     55,
    "install.setnet":     62,
    "install.secrets":    68,
    "install.postscript": 75,
    "install.roles":      85,
    "install.image":      90,
    "install.finalizing": 95,
    "install.success":    100,
    "install.booted":     100,
    # ponytail: transitional back-compat only. Nodes booted under the retired
    # trinity-booted-notify mechanism (pre-TRIX-1221 daemon rewrite) still have
    # this bare value sitting in monitor state until their next reprovision.
    # Drop once no live cluster has pre-rewrite state left.
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
    label = state.replace('install.', '')
    kind = 'done' if pct >= 100 else 'run'
    return pct, label, kind


# Booting nodes are bucketed into 3 coarse phases for the wave chart, not
# tracked by every individual install.* state (30 Jul 2026 redesign — "a few
# states, not all of them"). Boundaries match the pipeline order in STAGE_PCT:
# phase 1 runs up to (not including) install.downloaded, phase 2 up to (not
# including) install.unpack, phase 3 up to booted.
PHASE1_STATES = frozenset({
    'install.discovered', 'install.rendered', 'install.started', 'install.scripts',
    'install.prescript', 'install.setupbmc', 'install.partscript',
})
PHASE2_STATES = frozenset({'install.downloaded', 'install.download', 'install.completed'})
PHASE3_STATES = frozenset({
    'install.unpack', 'install.setnet', 'install.secrets', 'install.postscript',
    'install.roles', 'install.image', 'install.finalizing',
})


def classify_group(members, states):
    """[node names] + {name: raw_state} -> one Luna group's counts.

    booted/phase1/phase2/phase3 are what the UI renders (a wave chart split
    into 3 coarse phases, not all ~19 install.* states individually — see
    PHASE1/2/3_STATES above). 'failed' is explicit install.error for now.

    The previous design's STUCK_GAP_PCT ("this node is N points behind its
    fastest peer") does NOT carry over to this per-Luna-group granularity: a
    real group's own phase1/phase2/phase3 pcts span ~4 to ~95, so the instant
    even one member reaches booted (100%), every node still mid-pipeline is
    >=25 points behind it and would get flagged "stuck" purely for being
    normal and unfinished — caught by the demo() test below before this
    shipped. failedReasons keeps 'error' as its own key (not a bare bool) so
    a real staleness signal (e.g. no state change in N minutes) can be added
    as a second reason later without changing the shape callers already read.
    """
    scored = []
    for name in members:
        state = states.get(name)
        _pct, _label, kind = stage_of(state)
        scored.append((name, state, kind))

    booted, phase1, phase2, phase3 = [], [], [], []
    failed_reasons = {}
    for name, state, kind in scored:
        if kind == 'error':
            failed_reasons[name] = 'error'
        elif kind == 'done':
            booted.append(name)
        elif kind in ('idle', 'other'):
            # No monitor entry yet, or a state we don't recognize -- this is
            # not "before install.discovered and about to start", it's "we
            # don't know it's making progress at all". Counts as not booting
            # rather than inflating the booting wave with nodes that may not
            # be doing anything.
            failed_reasons[name] = 'not_started'
        elif state in PHASE2_STATES:
            phase2.append(name)
        elif state in PHASE3_STATES:
            phase3.append(name)
        else:  # PHASE1_STATES
            phase1.append(name)

    failed_nodes = sorted(failed_reasons)
    return {
        'total': len(members),
        'booted': len(booted),
        'booting': len(phase1) + len(phase2) + len(phase3),
        'phase1': len(phase1), 'phase2': len(phase2), 'phase3': len(phase3),
        'failed': len(failed_nodes),
        'failedNodes': failed_nodes,
        'failedReasons': failed_reasons,
        'overview': boot_overview(state for _name, state, _kind in scored),
        'funnel': boot_funnel(state for _name, state, _kind in scored),
    }


def boot_overview(raw_states):
    """Per-phase counts, the columns of `luna boot status`'s Boot Overview table,
    in the CLI's column order: unknown first, then the phases as the boot runs
    them, parked before done, done last."""
    phases = [phase for phase, _ in Boot.BOOT_PHASES if phase not in ('parked', 'done')]
    counts = dict.fromkeys(['unknown'] + phases + ['config', 'parked', 'done'], 0)
    for state in raw_states:
        counts[_BOOT.boot_phase(state)] += 1
    return counts


def boot_funnel(raw_states):
    """Nodes that reached at least each milestone, the bars of Boot Progress."""
    stages = [stage for stage in map(_BOOT.node_stage, raw_states) if stage is not None]
    return {label: sum(1 for stage in stages if stage >= threshold)
            for label, threshold, _note in Boot.BOOT_MILESTONES}


def _sum_group_counts(groups):
    totals = {'total': 0, 'booted': 0, 'booting': 0, 'failed': 0}
    for g in groups:
        for key in totals:
            totals[key] += g[key]
    return totals


def boot_view(monitor, nodes, scope):
    """The Boot Progress block and the Not Booted rows of `luna boot status -l`,
    computed by the CLI's own code for these nodes. node_states() is the one
    method of Boot that would call the daemon itself; it is given the monitor
    data this app already fetched (same shape: {node: {state, status, updated}}).
    None when no node in scope has reported a state, as the CLI returns."""
    boot = Boot.__new__(Boot)
    boot.args = {}
    boot.node_states = lambda: monitor
    progress = boot.boot_progress(scope)
    if progress is not None:
        progress['notBooted'] = boot.not_booted(nodes, scope)
    return progress


def build_images(nodes, states, all_osimage_names=(), all_groups=None, monitor=None):
    """nodes: {name: cfg}, states: {name: raw_state} -> list of image dicts
    (id, name, groups), most-active-first then by name. groups = real Luna
    node groups (node.group), each with its own booted/booting/failed counts —
    not provisioning-state buckets.

    all_osimage_names: every osimage Luna knows about, not just ones with
    nodes on them right now. An osimage with zero nodes still gets listed
    (empty groups) — a group with zero nodes still doesn't, since a group
    only exists here as a byproduct of nodes actually being in it.

    all_groups: {group: osimage} for every group Luna knows about. The ones
    with no nodes are listed by name in their osimage's unusedGroups, so the
    page can account for every image and group without inventing empty
    group rows.

    monitor: {node: {state, status, updated}} as the daemon's monitor route
    reports it; feeds each group's 'progress' block (see boot_view)."""
    monitor = monitor or {}
    by_image_group = defaultdict(lambda: defaultdict(list))
    for name, cfg in nodes.items():
        image = cfg.get('osimage') or 'unknown'
        group = cfg.get('group') or 'ungrouped'
        by_image_group[image][group].append(name)

    images = []
    for image, groupmap in sorted(by_image_group.items()):
        groups = []
        for group, members in sorted(groupmap.items()):
            sample = nodes[members[0]]
            counts = classify_group(members, states)
            groups.append({'name': group, 'network': _provision_network(sample), **counts,
                           'progress': boot_view(monitor, nodes, members)})
        images.append({
            'id': re.sub(r'[^A-Za-z0-9_-]', '-', image),
            'name': image,
            'groups': groups,
            'unusedGroups': [],
        })

    seen = {img['name'] for img in images}
    for image in sorted(set(all_osimage_names) - seen):
        images.append({'id': re.sub(r'[^A-Za-z0-9_-]', '-', image), 'name': image, 'groups': [], 'unusedGroups': []})

    used = {cfg.get('group') or 'ungrouped' for cfg in nodes.values()}
    by_name = {img['name']: img for img in images}
    for group, image in sorted((all_groups or {}).items()):
        if group in used:
            continue
        image = image or 'unknown'
        if image not in by_name:
            by_name[image] = {'id': re.sub(r'[^A-Za-z0-9_-]', '-', image), 'name': image,
                              'groups': [], 'unusedGroups': []}
            images.append(by_name[image])
        by_name[image]['unusedGroups'].append(group)

    all_booted = lambda img: all(g['failed'] == 0 and g['booting'] == 0 for g in img['groups']) if img['groups'] else True
    images.sort(key=lambda i: (all_booted(i), i['name']))
    return images


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

    try:
        osimage_data = api.get('/config/osimage')
        all_osimage_names = list(osimage_data.get('config', {}).get('osimage', {}) or {})
    except requests.HTTPError:
        all_osimage_names = []  # don't fail the whole page over this — nodes' own osimages still show

    try:
        group_data = api.get('/config/group')
        all_groups = {name: cfg.get('osimage') for name, cfg in
                      (group_data.get('config', {}).get('group', {}) or {}).items()}
    except requests.HTTPError:
        all_groups = {}  # same as osimages: unused groups just aren't listed

    states, monitor = {}, {}
    try:
        mon = api.get('/monitor/node')
        entries = mon.get('monitor', {}).get('status', {}).get('node', {}) or {}
        for name, info in entries.items():
            # bulk state is "<name> <raw-state>", e.g. "node001 install.image"
            raw = (info.get('state') or '').strip()
            if raw.startswith(name + ' '):
                raw = raw[len(name) + 1:]
            states[name] = raw or None
            monitor[name] = {'state': raw, 'status': info.get('status'), 'updated': info.get('updated')}
    except requests.HTTPError:
        pass  # 404 "no entries found" -> nothing provisioning right now

    return {
        'images': build_images(nodes, states, all_osimage_names, all_groups, monitor),
        'progress': boot_view(monitor, nodes, sorted(nodes)),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def _app_url():
    """Absolute pun-namespaced root for this app, used by the Vue SPA's
    window.APP_URL — same computation as the `node` app's Rest.app_url()."""
    full_url = f"{request.scheme}://{request.host}{request.path}"
    full_url = full_url[:-1]
    full_url_app = f"{full_url}{url_for('home')}"
    return full_url_app[:-1]


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html", APP_URL=_app_url())


@app.route('/api/status', methods=['GET'])
def status():
    try:
        return jsonify(get_status())
    except Exception as exc:  # surface API/config errors in the UI, don't 500
        app.logger.warning("status failed: %s", exc)
        return jsonify({"images": [], "progress": None, "error": str(exc)}), 200


def _sol_grab(node):
    """On-demand SOL capture via the sol-grab service (controller1). Never
    runs unbounded: the service itself caps concurrency and grab duration;
    this is just the call."""
    try:
        resp = requests.get(f'{SOL_GRAB_URL}/grab/{node}', timeout=SOL_GRAB_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        return {"lines": [], "error": f"sol-grab unreachable: {exc}"}


@app.route('/api/console/<node>', methods=['GET'])
def console(node):
    """Latest console output for one node, captured live over SOL. Empty is
    a valid, common state (a quiet console has nothing to say during the
    grab window) and is reported as such, not an error."""
    if not _NODE_NAME_RE.match(node):
        abort(404)

    result = _sol_grab(node)
    if result.get("error"):
        return jsonify({"node": node, "lines": [], "message": result["error"]}), 200
    if not result.get("lines"):
        return jsonify({"node": node, "lines": [], "message": "no console output captured yet"})
    return jsonify({"node": node, "lines": result["lines"], "source": "sol"})


@app.route('/license', methods=['GET'])
def license_info():
    """Human-readable license page (footer link opens this in a new tab)."""
    response = 'LICENSE Information is not available at this moment.'
    if os.path.isfile(LICENSE) and os.access(LICENSE, os.R_OK):
        with open(LICENSE, 'r', encoding='utf-8') as file_data:
            response = '<br />'.join(file_data.readlines())
    return response


if __name__ == "__main__":
    if APP_STATE is False:
        # devserver.py sits in the repository root, next to the app folders.
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from devserver import run_dev
        run_dev(app, port=7756)
    else:
        app.config["DEBUG"] = True
        app.run(host='0.0.0.0', port=7756, debug=True)


def demo():
    # ponytail: one runnable check for the pure logic (no network needed)
    assert stage_of(None) == (0, 'idle', 'idle')
    assert stage_of('install.booted') == (100, 'booted', 'done')
    assert stage_of('booted') == (100, 'booted', 'done')  # legacy pre-rewrite value
    assert stage_of('install.image')[0] == 90
    assert stage_of('install.setupbmc')[0] == 22
    assert stage_of('install.unpack')[0] == 55
    assert stage_of('install.error')[2] == 'error'

    def node(group, osimage='img', network='cluster'):
        return {'osimage': osimage, 'group': group, 'provision_method': 'torrent',
                'provision_interface': 'BOOTIF',
                'interfaces': [{'interface': 'BOOTIF', 'network': network}]}

    # Two nodes, same image, same group, one in phase1 one in phase2 -- not
    # merged with each other, and neither is "failed".
    nodes = {'node001': node('compute01'), 'node002': node('compute01')}
    images = build_images(nodes, {'node001': 'install.discovered', 'node002': 'install.downloaded'})
    assert len(images) == 1
    img = images[0]
    assert img['name'] == 'img'
    assert len(img['groups']) == 1
    g = img['groups'][0]
    assert g['name'] == 'compute01' and g['network'] == 'cluster'
    # overview columns are whatever the installed CLI's BOOT_PHASES says, so the
    # expectation is built from that table rather than spelled out
    def overview(**counts):
        return {**boot_overview([]), **counts}
    assert list(boot_overview([])) == ['unknown', 'ipxe', 'download', 'unpack', 'config', 'parked', 'done']
    assert g == {'name': 'compute01', 'network': 'cluster', 'total': 2, 'booted': 0,
                 'booting': 2, 'phase1': 1, 'phase2': 1, 'phase3': 0,
                 'failed': 0, 'failedNodes': [], 'failedReasons': {},
                 'overview': overview(download=1, config=1),
                 'funnel': {'discovered': 2, 'rendered': 1, 'prepared': 1, 'downloaded': 0,
                            'unpacked': 0, 'configured': 0, 'booted': 0},
                 'progress': None}, g

    # Two different Luna groups under the same image stay separate group cards.
    nodes2 = {'node001': node('compute01'), 'node002': node('compute02')}
    images2 = build_images(nodes2, {'node001': 'install.booted', 'node002': 'install.booted'})
    assert len(images2[0]['groups']) == 2
    by_name = {g['name']: g for g in images2[0]['groups']}
    assert by_name['compute01']['booted'] == 1 and by_name['compute02']['booted'] == 1

    # phase boundaries: discovered->downloaded is phase1, downloaded->unpack is
    # phase2, unpack->booted is phase3 -- exactly the 3 states asked for.
    nodes3 = {n: node('compute01') for n in ('node001', 'node002', 'node003', 'node004')}
    images3 = build_images(nodes3, {
        'node001': 'install.discovered', 'node002': 'install.downloaded',
        'node003': 'install.unpack', 'node004': 'install.booted',
    })
    g3 = images3[0]['groups'][0]
    assert (g3['phase1'], g3['phase2'], g3['phase3'], g3['booted']) == (1, 1, 1, 1), g3

    # overview/funnel use the CLI's own tables, so they match `luna boot status`,
    # quirks included: install.discovered sits under 'config' (the CLI's 'ipxe'
    # phase only matches 'rendered'), and a milestone counts as passed only once
    # the node is in the stage after it (install.downloaded has not passed
    # 'downloaded', install.unpack has).
    assert g3['overview'] == overview(download=1, unpack=1, done=1, config=1), g3['overview']
    assert g3['funnel'] == {'discovered': 4, 'rendered': 3, 'prepared': 3, 'downloaded': 2,
                            'unpacked': 1, 'configured': 1, 'booted': 1}, g3['funnel']

    # a node still early in the pipeline while a sibling has already booted is
    # NORMAL, not "failed" -- the regression this test exists to catch (an
    # earlier version of this function flagged it "stuck" purely for being
    # >=25 points behind a booted peer, which is true of almost every
    # mid-pipeline node the instant anyone in its group finishes).
    nodes4 = {n: node('compute01') for n in ('node001', 'node002', 'node003')}
    images4 = build_images(nodes4, {'node001': 'install.booted', 'node002': 'install.booted',
                                     'node003': 'install.discovered'})
    g4 = images4[0]['groups'][0]
    assert g4['failed'] == 0, g4
    assert g4['booted'] == 2 and g4['phase1'] == 1

    # only an explicit install.error counts as failed right now
    nodes5 = {n: node('compute01') for n in ('node001', 'node002', 'node003')}
    images5 = build_images(nodes5, {'node001': 'install.error', 'node002': 'install.booted',
                                     'node003': 'install.discovered'})
    g5 = images5[0]['groups'][0]
    assert g5['booted'] == 1 and g5['failed'] == 1
    assert g5['failedReasons'] == {'node001': 'error'}

    # a node with no monitor entry at all (never reached install.discovered)
    # counts as not booting, not as an early-phase booting node
    nodes6 = {n: node('compute01') for n in ('node001', 'node002')}
    images6 = build_images(nodes6, {'node001': 'install.discovered'})  # node002 has no entry
    g6 = images6[0]['groups'][0]
    assert g6['booting'] == 1 and g6['phase1'] == 1
    assert g6['failed'] == 1 and g6['failedReasons'] == {'node002': 'not_started'}
    # a node with no state is 'unknown' in the overview and reaches no milestone
    assert g6['overview']['unknown'] == 1 and g6['overview']['config'] == 1, g6['overview']
    assert g6['funnel']['discovered'] == 1 and g6['funnel']['booted'] == 0, g6['funnel']

    # an osimage with zero nodes still gets listed (empty groups) when we know
    # about it from Luna's own osimage list; a group with zero nodes still
    # never gets synthesized, since groups only exist as a byproduct of nodes
    nodes7 = {'node001': node('rack01')}
    images7 = build_images(nodes7, {'node001': 'install.booted'},
                            all_osimage_names=['img', 'unused-image'])
    by_name7 = {i['name']: i for i in images7}
    assert set(by_name7) == {'img', 'unused-image'}, by_name7
    assert by_name7['unused-image']['groups'] == []

    # groups with no nodes are named under their own osimage's unusedGroups,
    # including an osimage nothing else references; groups with nodes are not
    images8 = build_images(nodes7, {'node001': 'install.booted'}, all_osimage_names=['img'],
                           all_groups={'rack01': 'img', 'rack02': 'img', 'spare': 'other-image'})
    by_name8 = {i['name']: i for i in images8}
    assert by_name8['img']['unusedGroups'] == ['rack02'], by_name8
    assert [g['name'] for g in by_name8['img']['groups']] == ['rack01']
    assert by_name8['other-image'] == {'id': 'other-image', 'name': 'other-image',
                                       'groups': [], 'unusedGroups': ['spare']}, by_name8

    # the progress block is the CLI's own luna boot status -l, fed with monitor
    # rows: cohort anchored on the in-flight node, a parked node is not in
    # flight, sanitized counts as done, a silent node is stuck, a 500 is failed
    from datetime import datetime, timedelta
    stamp = lambda minutes_ago: (datetime.utcnow() - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
    nodes9 = {n: node('compute01') for n in ('node001', 'node002', 'node003', 'node004', 'node005')}
    monitor9 = {
        'node001': {'state': 'install.booted', 'status': '200', 'updated': stamp(3)},
        'node002': {'state': 'install.unpack', 'status': '200', 'updated': stamp(2)},
        'node003': {'state': 'install.fatal', 'status': '200', 'updated': stamp(95)},
        'node004': {'state': 'install.sanitized', 'status': '200', 'updated': stamp(40)},
        'node005': {'state': 'install.discovered', 'status': '200', 'updated': stamp(120)},
    }
    states9 = {name: row['state'] for name, row in monitor9.items()}
    result9 = build_images(nodes9, states9, monitor=monitor9)
    g9 = result9[0]['groups'][0]
    assert g9['overview'] == overview(unpack=1, parked=1, done=2, config=1), g9['overview']
    p9 = g9['progress']
    assert p9['nodes'] == 5 and p9['anchored'] is True, p9
    assert [s['node'] for s in p9['stuck']] == ['node005'], p9['stuck']
    assert {m['milestone']: m['nodes'] for m in p9['milestones']}['booted'] == 1
    by_node = {row['node']: row for row in p9['notBooted']}
    assert set(by_node) == {'node002', 'node003', 'node004', 'node005'}, by_node
    assert by_node['node002']['condition'] == '' and by_node['node002']['stage'] == 'unpack'
    assert by_node['node003']['condition'] == 'parked' and by_node['node003']['step'] == 'fatal'
    assert by_node['node004']['condition'] == 'sanitized'
    assert by_node['node005']['condition'] == 'stuck' and by_node['node005']['minutes'] >= 120
    # a 500 from the installer is what the daemon classes as failed
    monitor9['node002']['status'] = '500'
    assert {r['node']: r['condition'] for r in boot_view(monitor9, nodes9, ['node002'])['notBooted']} == {'node002': 'failed'}
    # no monitor rows at all: no cohort, no block -- the CLI's None, not a crash
    assert boot_view({}, nodes9, list(nodes9)) is None

    print("OK: nodeboot logic (stage map, phase mapping, per-group build, no false-positive failures)")
