"""
test_fabric_errors.py — TRIX-1924

The app used to run ibnetdiscover on every cluster and hand its raw libibnetdisc
output to the user as a red error, which is what a cluster without InfiniBand
saw. These tests pin what it does instead: recognise why the fabric cannot be
scanned, skip the scan, and describe the remaining failures in a sentence.
"""

import subprocess

import pytest


# ── the pre-flight check ─────────────────────────────────────────────────

def _fake_glob(monkeypatch, app_module, mapping):
    # the class listing and the umad devices are faked; the port files under a faked
    # device are real files in tmp_path, so the link-layer read goes through glob as is
    real_glob = app_module.glob.glob
    monkeypatch.setattr(app_module.glob, 'glob',
                        lambda pattern: mapping[pattern] if pattern in mapping else real_glob(pattern))


def _device(tmp_path, name, link_layer):
    """An RDMA device as sysfs shows it: one port, its link_layer file."""
    port = tmp_path / name / 'ports' / '1'
    port.mkdir(parents=True)
    (port / 'link_layer').write_text(f'{link_layer}\n')
    return str(tmp_path / name)


def test_no_hardware_is_informational(app_module, monkeypatch):
    _fake_glob(monkeypatch, app_module, {})
    notice = app_module.fabric_unavailable()
    assert notice['level'] == 'info'
    assert 'No InfiniBand hardware' in notice['message']


def test_empty_sysfs_directory_counts_as_no_hardware(app_module, monkeypatch):
    # /sys/class/infiniband exists on machines with no InfiniBand at all, so the
    # entries decide. Testing the directory instead would never fire.
    _fake_glob(monkeypatch, app_module, {'/sys/class/infiniband/*': []})
    assert app_module.fabric_unavailable()['level'] == 'info'


def test_hardware_without_umad_names_the_module(app_module, monkeypatch, tmp_path):
    _fake_glob(monkeypatch, app_module, {'/sys/class/infiniband/*': [_device(tmp_path, 'mlx5_0', 'InfiniBand')]})
    notice = app_module.fabric_unavailable()
    assert notice['level'] == 'warning'
    assert 'ib_umad' in notice['message']


def test_umad_without_access_is_reported_separately(app_module, monkeypatch, tmp_path):
    _fake_glob(monkeypatch, app_module, {
        '/sys/class/infiniband/*': [_device(tmp_path, 'mlx5_0', 'InfiniBand')],
        '/dev/infiniband/umad*': ['/dev/infiniband/umad0'],
    })
    monkeypatch.setattr(app_module.os, 'access', lambda path, mode: False)
    notice = app_module.fabric_unavailable()
    assert notice['level'] == 'warning'
    assert 'not readable and writable' in notice['message']


def test_usable_fabric_gives_no_notice(app_module, monkeypatch, tmp_path):
    _fake_glob(monkeypatch, app_module, {
        '/sys/class/infiniband/*': [_device(tmp_path, 'mlx5_0', 'InfiniBand')],
        '/dev/infiniband/umad*': ['/dev/infiniband/umad0'],
    })
    monkeypatch.setattr(app_module.os, 'access', lambda path, mode: True)
    assert app_module.fabric_unavailable() is None


def test_rdma_ethernet_adapters_are_not_infiniband(app_module, monkeypatch, tmp_path):
    # Intel X722 ports register under /sys/class/infiniband through irdma with an
    # Ethernet link layer; they have no subnet manager, so there is nothing to scan
    _fake_glob(monkeypatch, app_module, {
        '/sys/class/infiniband/*': [_device(tmp_path, f'irdma{n}', 'Ethernet') for n in range(4)],
    })
    notice = app_module.fabric_unavailable()
    assert notice['level'] == 'info'
    assert 'No InfiniBand hardware' in notice['message']
    assert 'irdma0, irdma1, irdma2, irdma3' in notice['message']


def test_one_infiniband_port_beside_ethernet_adapters_counts(app_module, monkeypatch, tmp_path):
    _fake_glob(monkeypatch, app_module, {
        '/sys/class/infiniband/*': [_device(tmp_path, 'irdma0', 'Ethernet'), _device(tmp_path, 'mlx5_0', 'InfiniBand')],
    })
    assert 'ib_umad' in app_module.fabric_unavailable()['message']


# ── the route ────────────────────────────────────────────────────────────

def test_graph_route_skips_the_scan_when_there_is_no_fabric(client, app_module, monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("ibnetdiscover must not run when there is no fabric")

    monkeypatch.setattr(app_module.subprocess, 'run', refuse)
    monkeypatch.setattr(app_module, 'fabric_unavailable',
                        lambda: {'level': 'info', 'message': 'No InfiniBand hardware was found.'})

    response = client.get('/graph')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['nodes'] == [] and payload['links'] == []
    assert payload['notice']['level'] == 'info'


def test_graph_route_still_renders_a_fabric(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, 'fabric_unavailable', lambda: None)
    monkeypatch.setattr(app_module, 'get_graph_data', lambda: SWITCH_AND_HOST)
    monkeypatch.setattr(app_module, 'get_prometheus_data', lambda: {})

    payload = client.get('/graph').get_json()

    assert 'notice' not in payload
    assert [node['name'] for node in payload['nodes']] == ['switch01', 'node001 HCA-1']
    assert len(payload['links']) == 1


# ── the scan failures that are left ──────────────────────────────────────

class _Completed:
    def __init__(self, returncode, stderr):
        self.returncode = returncode
        self.stdout = b''
        self.stderr = stderr.encode('utf-8')


def test_missing_command_names_the_package(app_module, monkeypatch):
    monkeypatch.setattr(app_module.subprocess, 'run',
                        lambda *a, **kw: _Completed(127, 'sh: ibnetdiscover: command not found'))
    with pytest.raises(Exception) as exc:
        app_module.get_graph_data()
    assert 'infiniband-diags' in str(exc.value)


def test_scan_failure_leads_with_a_sentence_and_keeps_the_output(app_module, monkeypatch):
    stderr = "ibwarn: [25699] get_abi_version: can't read ABI version from <abi_version>"
    monkeypatch.setattr(app_module.subprocess, 'run', lambda *a, **kw: _Completed(255, stderr))
    with pytest.raises(Exception) as exc:
        app_module.get_graph_data()
    message = str(exc.value)
    assert message.startswith('The InfiniBand fabric scan failed (exit code 255).')
    assert '&lt;abi_version&gt;' in message and '<abi_version>' not in message


def test_scan_is_bounded_by_the_configured_timeout(app_module, monkeypatch, settings):
    seen = {}

    def record(*args, **kwargs):
        seen.update(kwargs)
        raise subprocess.TimeoutExpired(cmd='ibnetdiscover', timeout=kwargs['timeout'])

    monkeypatch.setattr(app_module.subprocess, 'run', record)
    with pytest.raises(Exception) as exc:
        app_module.get_graph_data()
    assert seen['timeout'] == settings['IBNETDISCOVER_TIMEOUT']
    assert 'did not finish within' in str(exc.value)


# ── the settings the code indexes must exist in the shipped file ─────────

def test_every_app_setting_the_code_uses_is_shipped(app_module, settings, settings_path):
    import re
    source = open(app_module.__file__.replace('.pyc', '.py'), encoding='utf-8').read()
    used = set(re.findall(r"CONFIGS\['APP'\]\['(\w+)'\]", source))
    assert used, "no APP settings found — the pattern this test scans for has changed"
    assert used <= set(settings), f"missing from {settings_path}: {used - set(settings)}"


# ── every template the app renders must be shipped with it ───────────────

def test_every_rendered_template_exists(app_module):
    import os
    import re
    source = open(app_module.__file__.replace('.pyc', '.py'), encoding='utf-8').read()
    rendered = set(re.findall(r'render_template\(\s*["\'](.+?)["\']', source))
    assert rendered, "no rendered templates found — the pattern this test scans for has changed"
    template_dir = os.path.join(os.path.dirname(app_module.__file__), 'templates')
    missing = [name for name in rendered if not os.path.isfile(os.path.join(template_dir, name))]
    assert not missing, f"rendered but not shipped: {missing}"


SWITCH_AND_HOST = """
Switch\t36 "S-0000000000000001"\t\t# "switch01" base port 0
[1]\t"H-0000000000000002"[1]\t\t# "node001 HCA-1"

Ca\t1 "H-0000000000000002"\t\t# "node001 HCA-1"
[1]\t"S-0000000000000001"[1]\t\t# "switch01"
"""
