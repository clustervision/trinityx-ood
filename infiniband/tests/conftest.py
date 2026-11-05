"""
conftest.py — pytest fixtures for the TrinityX OOD Infiniband app.

Package strategy
----------------
base.config   — stubbed (avoids the /trinity/local/… luna.ini and a live token)
rest, helper  — stubbed (avoid live Luna daemon and Slurm calls)
hostlist      — stubbed when not installed

The settings the stub hands back are read from the app's own app.toml where
toml is importable, so a test can never pass against a value the shipped
configuration does not actually carry.
"""

import logging
import os
import re
import sys
import types

import pytest

# ── Make the infiniband/ directory importable ────────────────────────────
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, APP_DIR)

APP_TOML = os.path.join(APP_DIR, 'base', 'settings', 'app.toml')


def app_toml_settings():
    """The shipped app settings, parsed by toml where it is available."""
    try:
        import toml
        return toml.load(APP_TOML)
    except ImportError:
        raw = open(APP_TOML, encoding='utf-8').read()
        settings = {}
        for key, value in re.findall(r'^(\w+)\s*=\s*(.+)$', raw, re.M):
            value = value.strip()
            settings[key] = int(value) if value.isdigit() else value.strip('"')
        return settings


# ── base.config — stubbed, no luna.ini and no token fetch ────────────────
_base_config = types.ModuleType('base.config')
_base_config.get_configs = lambda: {
    'APP': app_toml_settings(),
    'LUNA': {},
    'ENV': {},
}
sys.modules['base.config'] = _base_config

# ── log — stubbed, /var/log/luna is not writable outside the controller ──
# The real Log.init_log exits the process when it cannot open the log file, so
# without this the suite would only pass where something else had already
# configured logging.
_log = types.ModuleType('log')
_log.Log = type('Log', (), {
    'init_log': classmethod(lambda cls, level=None: logging.getLogger('luna2-web-test')),
    'get_logger': classmethod(lambda cls: logging.getLogger('luna2-web-test')),
})
sys.modules['log'] = _log

# ── rest / helper — stubbed, no live daemon ──────────────────────────────
_rest = types.ModuleType('rest')
_rest.Rest = type('Rest', (), {})
sys.modules['rest'] = _rest

_helper = types.ModuleType('helper')
_helper.Helper = type('Helper', (), {'slurm_info': lambda self: {'status': False, 'response': ''}})
sys.modules['helper'] = _helper

# ── hostlist — stubbed only when the real one is absent ──────────────────
try:
    import hostlist  # noqa — just verify importable
except ImportError:
    _hostlist = types.ModuleType('hostlist')
    _hostlist.expand_hostlist = lambda spec: [spec]
    _hostlist.collect_hostlist = lambda names: ','.join(names)
    sys.modules['hostlist'] = _hostlist


@pytest.fixture
def app_module():
    """The application module, imported once the stubs above are in place."""
    import app
    return app


@pytest.fixture
def client(app_module, tmp_path, monkeypatch):
    """A test client whose home/ini validation passes, so routes are reachable."""
    ini_file = tmp_path / 'luna.ini'
    ini_file.write_text('[API]\n')
    monkeypatch.setattr(app_module, 'INI_FILE', str(ini_file))
    monkeypatch.setattr(app_module, 'TOKEN_FILE', str(tmp_path / '.luna-token.dat'))
    monkeypatch.setattr(app_module, 'STATE_PATH', str(tmp_path / 'state.json'))
    return app_module.app.test_client()


@pytest.fixture
def settings():
    """The settings the shipped app.toml actually carries."""
    return app_toml_settings()


@pytest.fixture
def settings_path():
    return APP_TOML
