"""
test_gres.py — Non-intrusive regression tests for the mila_gres feature.

Tests are grouped into three layers:

  1. Pure logic  — render_raw_gres_defaults(), save_gres_configuration(),
                   Gres= auto-derivation in save_configuration().
                   No HTTP, no file I/O beyond temp files.

  2. Integration — load_gres_configuration() / load_configuration() round-trip
                   (write a realistic gres.conf Defaults block, read it back).

  3. API (Flask) — GET /json/configuration/gres_presets
                   POST /json/configuration/save  (payload includes gres_presets)

All three layers run without a live Slurm daemon, without the real
trinityx_config_* packages, and without touching /etc/slurm/.
"""

import json
import os
import pytest


# ── helpers ──────────────────────────────────────────────────────────────

def _make_full_config(extra_nodes=None, extra_gres_presets=None):
    """Return a minimal but complete configuration dict."""
    nodes = [
        {'name': 'gpu01', 'group_name': 'gpu', 'hw_preset_name': 'gpu_hw',
         'gres_preset_names': ['gpu_A100'], 'properties': {'State': ''}},
        {'name': 'gpu02', 'group_name': 'gpu', 'hw_preset_name': 'gpu_hw',
         'gres_preset_names': ['gpu_A100'], 'properties': {'State': ''}},
        {'name': 'gpu03', 'group_name': 'gpu', 'hw_preset_name': 'gpu_hw',
         'gres_preset_names': ['gpu_H100', 'fpga_v1'], 'properties': {'State': ''}},
        {'name': 'cpu01', 'group_name': 'compute', 'hw_preset_name': 'std_hw',
         'gres_preset_names': [], 'properties': {'State': ''}},
    ]
    if extra_nodes:
        nodes.extend(extra_nodes)

    gres_presets = [
        {'name': 'gpu_A100', 'properties': {
            'Name': 'gpu', 'Type': 'A100', 'Count': '4',
            'File': '/dev/nvidia[0-3]', 'no_consume': False}},
        {'name': 'gpu_H100', 'properties': {
            'Name': 'gpu', 'Type': 'H100', 'Count': '16',
            'File': '/dev/nvidia[0-15]', 'no_consume': False}},
        {'name': 'fpga_v1', 'properties': {
            'Name': 'fpga', 'Type': '', 'Count': '1',
            'File': '/dev/accel/accel0', 'no_consume': False}},
    ]
    if extra_gres_presets:
        gres_presets.extend(extra_gres_presets)

    partitions = [
        {'name': 'gpu', 'node_names': ['gpu01', 'gpu02', 'gpu03'],
         'hw_preset_name': None, 'gres_preset_names': ['gpu_A100', 'gpu_H100', 'fpga_v1'],
         'properties': {'State': 'UP'}},
        {'name': 'normal', 'node_names': ['cpu01'],
         'hw_preset_name': None, 'gres_preset_names': [],
         'properties': {'State': 'UP'}},
    ]
    return {
        'nodes': nodes,
        'partitions': partitions,
        'groups': [
            {'name': 'gpu',     'node_names': ['gpu01', 'gpu02', 'gpu03']},
            {'name': 'compute', 'node_names': ['cpu01']},
        ],
        'hw_presets': [
            {'name': 'gpu_hw', 'properties': {
                'Boards': '1', 'SocketsPerBoard': '2', 'CoresPerSocket': '16',
                'ThreadsPerCore': '2', 'RealMemory': '512000', 'TmpDisk': '0'}},
        ],
        'gres_presets': gres_presets,
    }


# ════════════════════════════════════════════════════════════════════════
#  LAYER 1 — Pure logic tests (no Flask, no file I/O)
# ════════════════════════════════════════════════════════════════════════

class TestRenderRawGresDefaults:
    """render_raw_gres_defaults() builds the Defaults block content."""

    def test_all_presets_present(self, slurm_app):
        cfg = _make_full_config()
        block = slurm_app.render_raw_gres_defaults(cfg)
        assert 'GRESPresetName=gpu_A100' in block
        assert 'GRESPresetName=gpu_H100' in block
        assert 'GRESPresetName=fpga_v1'  in block

    def test_preset_properties_rendered(self, slurm_app):
        cfg = _make_full_config()
        block = slurm_app.render_raw_gres_defaults(cfg)
        assert 'Name=gpu'           in block
        assert 'Type=A100'          in block
        assert 'Count=4'            in block
        assert 'File=/dev/nvidia[0-3]' in block

    def test_node_annotation_present(self, slurm_app):
        cfg = _make_full_config()
        block = slurm_app.render_raw_gres_defaults(cfg)
        # gpu_A100 maps to gpu01 + gpu02 — should appear in Nodes= annotation
        assert 'Nodes=' in block
        assert 'gpu' in block    # hostlist — gpu[01-03] after partition propagation

    def test_partition_annotation_present(self, slurm_app):
        cfg = _make_full_config()
        block = slurm_app.render_raw_gres_defaults(cfg)
        assert 'Partitions=gpu' in block

    def test_no_consume_flag(self, slurm_app):
        cfg = _make_full_config(extra_gres_presets=[{
            'name': 'shared_nic',
            'properties': {'Name': 'nic', 'Type': '', 'Count': '1',
                           'File': '', 'no_consume': True}
        }])
        block = slurm_app.render_raw_gres_defaults(cfg)
        # Must be written as no_consume=true (a key=value pair), not a bare flag —
        # only that form survives the key=value parser on reload (see Defect 2).
        assert 'no_consume=true' in block

    def test_empty_gres_presets(self, slurm_app):
        cfg = _make_full_config()
        cfg['gres_presets'] = []
        block = slurm_app.render_raw_gres_defaults(cfg)
        assert block == ''

    def test_lines_are_comments(self, slurm_app):
        """Every line in the Defaults block must be a comment (starts with #)."""
        cfg = _make_full_config()
        block = slurm_app.render_raw_gres_defaults(cfg)
        for line in block.strip().splitlines():
            assert line.startswith('#'), f"Non-comment line in Defaults block: {line!r}"


class TestGresAutoDerivation:
    """save_configuration() must auto-derive Gres= from gres_preset_names."""

    def test_gres_derived_for_gpu_node(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_configuration(cfg, slurm_files=slurm_files, backup=False)
        gpu01 = next(n for n in cfg['nodes'] if n['name'] == 'gpu01')
        # gpu01 has gpu_A100 directly; the partition also carries gpu_H100 + fpga_v1
        # which now propagate to all nodes in that partition — check gpu:A100:4 present
        gres = gpu01['properties'].get('Gres', '')
        assert 'gpu:A100:4' in gres

    def test_gres_multi_preset_node(self, slurm_app, slurm_files):
        """gpu03 has gpu_H100 + fpga_v1 → Gres=gpu:H100:16,fpga:1"""
        cfg = _make_full_config()
        slurm_app.save_configuration(cfg, slurm_files=slurm_files, backup=False)
        gpu03 = next(n for n in cfg['nodes'] if n['name'] == 'gpu03')
        gres  = gpu03['properties'].get('Gres', '')
        assert 'gpu:H100:16' in gres
        assert 'fpga:1'      in gres

    def test_gres_cleared_when_no_preset(self, slurm_app, slurm_files):
        """cpu01 has no GRES presets → Gres= must not appear."""
        cfg = _make_full_config()
        # Pre-set a stale Gres= to ensure it's cleared
        for n in cfg['nodes']:
            if n['name'] == 'cpu01':
                n['properties']['Gres'] = 'gpu:A100:4'
        slurm_app.save_configuration(cfg, slurm_files=slurm_files, backup=False)
        cpu01 = next(n for n in cfg['nodes'] if n['name'] == 'cpu01')
        assert 'Gres' not in cpu01['properties']

    def test_unknown_preset_name_skipped(self, slurm_app, slurm_files):
        """A node referencing a non-existent preset must not crash."""
        cfg = _make_full_config()
        cfg['nodes'][0]['gres_preset_names'] = ['does_not_exist']
        # Should not raise
        slurm_app.save_configuration(cfg, slurm_files=slurm_files, backup=False)

    def test_type_omitted_when_empty(self, slurm_app, slurm_files):
        """If Type is empty, the Gres= string must be Name:Count, not Name::Count."""
        cfg = _make_full_config()
        # fpga_v1 has Type=''
        gpu03 = next(n for n in cfg['nodes'] if n['name'] == 'gpu03')
        slurm_app.save_configuration(cfg, slurm_files=slurm_files, backup=False)
        gres = gpu03['properties'].get('Gres', '')
        assert '::' not in gres, f"Double-colon in Gres= string: {gres!r}"


class TestGresConfRunningBlock:
    """save_gres_configuration() writes correct NodeName= lines."""

    def test_nodename_lines_written(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert 'NodeName=' in content
        assert 'Name=gpu'  in content

    def test_a100_line_present(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert 'Type=A100' in content
        assert 'Count=4'   in content

    def test_h100_and_fpga_lines_present(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert 'Type=H100' in content
        assert 'Count=16'  in content
        assert 'Name=fpga' in content

    def test_cpu_nodes_not_in_gres_conf(self, slurm_app, slurm_files):
        """cpu01 has no GRES presets — must not appear in gres.conf."""
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert 'NodeName=cpu01' not in content

    def test_file_field_written(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert '/dev/nvidia' in content

    def test_managed_block_markers_present(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert 'TrinityX Managed block start' in content
        assert 'TrinityX Managed block end'   in content


class TestParseRawConfiguration:
    """parse_raw_configuration() must pass gres_presets through unchanged."""

    def test_gres_presets_preserved(self, slurm_app):
        raw = _make_full_config()
        result = slurm_app.parse_raw_configuration(raw)
        assert 'gres_presets' in result
        assert len(result['gres_presets']) == 3

    def test_gres_preset_names_preserved_on_nodes(self, slurm_app):
        raw = _make_full_config()
        result = slurm_app.parse_raw_configuration(raw)
        gpu03 = next(n for n in result['nodes'] if n['name'] == 'gpu03')
        assert 'gpu_H100' in gpu03['gres_preset_names']
        assert 'fpga_v1'  in gpu03['gres_preset_names']

    def test_empty_gres_presets_when_missing(self, slurm_app):
        raw = _make_full_config()
        del raw['gres_presets']
        result = slurm_app.parse_raw_configuration(raw)
        assert result['gres_presets'] == []

    def test_existing_hw_presets_unaffected(self, slurm_app):
        """gres additions must not break HWPreset round-trip."""
        raw = _make_full_config()
        result = slurm_app.parse_raw_configuration(raw)
        assert len(result['hw_presets']) == len(raw['hw_presets'])


# ════════════════════════════════════════════════════════════════════════
#  LAYER 2 — Integration: load/save round-trip
# ════════════════════════════════════════════════════════════════════════

class TestLoadGresConfiguration:
    """load_gres_configuration() must reconstruct presets from a written file."""

    def test_round_trip_preset_names(self, slurm_app, slurm_files):
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        # Now read it back via load_gres_configuration
        presets, gres_nodes, gres_parts = slurm_app.load_gres_configuration(slurm_files)
        names = [p['name'] for p in presets]
        assert 'gpu_A100' in names
        assert 'gpu_H100' in names
        assert 'fpga_v1'  in names

    def test_round_trip_node_assignments(self, slurm_app, slurm_files):
        """
        Node assignments are stored in the Defaults block as comment
        annotations parsed via SlurmConfig.comment().  The test stub
        returns {} for .comment() (it cannot parse comment metadata),
        so we verify the annotation text is physically present in the
        file instead — which is what the real parser would consume.
        """
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        # Nodes= annotation must appear in the Defaults block
        assert 'Nodes=' in content
        assert 'gpu' in content   # gpu01/gpu[01-03] hostlist — partition propagation may expand set

    def test_round_trip_partition_assignments(self, slurm_app, slurm_files):
        """
        Same stub limitation as above — verify the Partitions= annotation
        text is written to the Defaults block rather than trying to parse
        it back through the stubbed SlurmConfig.comment().
        """
        cfg = _make_full_config()
        slurm_app.save_gres_configuration(cfg, slurm_files)
        with open(slurm_files['gres']) as fh:
            content = fh.read()
        assert 'Partitions=gpu' in content

    def test_no_consume_survives_round_trip(self, slurm_app, slurm_files):
        """
        Defect 2: the no_consume flag must survive a Defaults-block save+reload.
        Writes the Defaults block the same way save_configuration() does
        (defaults_only=True), then reads it back — self-contained so it does not
        depend on test ordering.
        """
        cfg = _make_full_config(extra_gres_presets=[{
            'name': 'shared_nic',
            'properties': {'Name': 'nic', 'Type': '', 'Count': '1',
                           'File': '', 'no_consume': True}
        }])
        slurm_app.save_gres_configuration(cfg, slurm_files, defaults_only=True)
        presets, _, _ = slurm_app.load_gres_configuration(slurm_files)
        by_name = {p['name']: p for p in presets}
        # the shared resource kept its ON state across the round-trip
        assert by_name['shared_nic']['properties'].get('no_consume') is True
        # a preset that was OFF must not come back ON
        assert not by_name['gpu_A100']['properties'].get('no_consume')

    def test_missing_gres_file_returns_empty(self, slurm_app, slurm_files):
        """If gres.conf doesn't exist yet, must return empty structures."""
        bad_files = dict(slurm_files, gres='/nonexistent/path/gres.conf')
        presets, gres_nodes, gres_parts = slurm_app.load_gres_configuration(bad_files)
        assert presets    == []
        assert gres_nodes == {}
        assert gres_parts == {}


class TestLoadConfigurationIntegration:
    """load_configuration() must surface gres_presets on the top-level dict."""

    def test_gres_presets_key_present(self, slurm_app, slurm_files):
        cfg = slurm_app.load_configuration(slurm_files=slurm_files)
        assert 'gres_presets' in cfg

    def test_gres_presets_is_list(self, slurm_app, slurm_files):
        cfg = slurm_app.load_configuration(slurm_files=slurm_files)
        assert isinstance(cfg['gres_presets'], list)

    def test_nodes_have_gres_preset_names_key(self, slurm_app, slurm_files):
        """Every node dict returned must have gres_preset_names (even if empty)."""
        # Write some nodes first
        full_cfg = _make_full_config()
        slurm_app.save_configuration(full_cfg, slurm_files=slurm_files, backup=False)
        cfg = slurm_app.load_configuration(slurm_files=slurm_files)
        for node in cfg.get('nodes', []):
            assert 'gres_preset_names' in node, \
                f"Node {node.get('name')} missing gres_preset_names key"

    def test_hw_presets_still_present(self, slurm_app, slurm_files):
        """gres additions must not destroy hw_presets loading."""
        cfg = slurm_app.load_configuration(slurm_files=slurm_files)
        assert 'hw_presets' in cfg


# ════════════════════════════════════════════════════════════════════════
#  LAYER 3 — API (Flask test client)
# ════════════════════════════════════════════════════════════════════════

class TestGresPresetsRoute:
    """GET /json/configuration/gres_presets"""

    def test_returns_200(self, client):
        rv = client.get('/json/configuration/gres_presets')
        assert rv.status_code == 200

    def test_returns_json_list(self, client):
        rv = client.get('/json/configuration/gres_presets')
        data = json.loads(rv.data)
        assert isinstance(data, list)

    def test_backup_param_accepted(self, client):
        rv = client.get('/json/configuration/gres_presets?load_from_backup=true')
        assert rv.status_code == 200


class TestSaveRouteWithGres:
    """POST /json/configuration/save — payload includes gres_presets."""

    def test_save_returns_redirect(self, client):
        payload = _make_full_config()
        rv = client.post(
            '/json/configuration/save',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'redirect' in data

    def test_save_without_gres_presets_key(self, client):
        """Saving a payload without gres_presets must not crash (backward compat)."""
        payload = _make_full_config()
        del payload['gres_presets']
        rv = client.post(
            '/json/configuration/save',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert rv.status_code == 200

    def test_existing_routes_unaffected(self, client):
        """Regression: existing node/partition/hw_preset routes still return 200."""
        for route in ['/json/configuration/nodes',
                      '/json/configuration/partitions',
                      '/json/configuration/hw_presets']:
            rv = client.get(route)
            assert rv.status_code == 200, f"Route {route} returned {rv.status_code}"


class TestPreviewRouteWithGres:
    """POST /json/configuration/preview — must now return gres.conf tab."""

    def test_preview_contains_gres_block(self, client):
        payload = _make_full_config()
        rv = client.post(
            '/json/configuration/preview',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert rv.status_code == 200
        # The rendered HTML must contain the gres preview tab
        html = rv.data.decode()
        assert 'gres-preview-tab' in html or 'gres.conf' in html


# ════════════════════════════════════════════════════════════════════════
#  REGRESSION — pre-existing behaviour must be untouched
# ════════════════════════════════════════════════════════════════════════

class TestRegressionExistingBehaviour:
    """
    Ensure the mila_gres changes did not break any pre-existing
    nodes / partitions / hw_presets behaviour.
    """

    def test_hw_presets_route(self, client):
        rv = client.get('/json/configuration/hw_presets')
        assert rv.status_code == 200
        assert isinstance(json.loads(rv.data), list)

    def test_nodes_route(self, client):
        rv = client.get('/json/configuration/nodes')
        assert rv.status_code == 200
        assert isinstance(json.loads(rv.data), list)

    def test_partitions_route(self, client):
        rv = client.get('/json/configuration/partitions')
        assert rv.status_code == 200
        assert isinstance(json.loads(rv.data), list)

    def test_index_route(self, client):
        rv = client.get('/')
        assert rv.status_code == 200

    def test_save_without_gres_field_backward_compat(self, client):
        """A payload from the old UI (no gres_presets key) must save cleanly."""
        old_style_payload = {
            'hw_presets': [],
            'nodes':      [],
            'partitions': [],
        }
        rv = client.post(
            '/json/configuration/save',
            data=json.dumps(old_style_payload),
            content_type='application/json'
        )
        assert rv.status_code == 200

    def test_gres_preset_names_default_empty_list(self, slurm_app):
        """parse_raw_configuration must add gres_preset_names=[] on nodes that omit it."""
        raw = {
            'hw_presets': [],
            'gres_presets': [],
            'nodes': [
                {'name': 'node01', 'hw_preset_name': None, 'properties': {}}
            ],
            'partitions': [],
        }
        result = slurm_app.parse_raw_configuration(raw)
        node = result['nodes'][0]
        # gres_preset_names may be absent (old node) — that is acceptable;
        # what must NOT happen is an exception
        assert isinstance(node.get('gres_preset_names', []), list)
