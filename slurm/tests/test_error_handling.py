"""
test_error_handling.py — TRIX-1883

Regression tests for the error paths that used to kill the WSGI worker with
sys.exit() (surfacing as a bare 'error' in OnDemand) or render a non-existent
error.html. They must now raise a descriptive Exception so the global
wrap_errors handler returns {"message": ...}.
"""

import os
import importlib.util
import tempfile

import pytest
import requests


def _load_real_module(name, relpath):
    """Load a base.* module straight from disk, bypassing conftest stubs."""
    path = os.path.join(os.path.dirname(__file__), '..', relpath)
    spec = importlib.util.spec_from_file_location(name, os.path.abspath(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ini_module = _load_real_module('real_base_ini', 'base/ini.py')
token_module = _load_real_module('real_base_token', 'base/token.py')
Ini = ini_module.Ini
Token = token_module.Token


# ── base.ini.Ini.read_ini ────────────────────────────────────────────────

def test_read_ini_missing_file_raises_not_exits():
    with pytest.raises(Exception) as exc:
        Ini.read_ini('/nonexistent/luna.ini')
    assert not isinstance(exc.value, SystemExit)
    assert 'not found on this machine' in str(exc.value)


def test_read_ini_missing_api_section_raises():
    with tempfile.NamedTemporaryFile('w', suffix='.ini', delete=False) as fh:
        fh.write('[OTHER]\nfoo = bar\n')
        path = fh.name
    try:
        with pytest.raises(Exception) as exc:
            Ini.read_ini(path)
        assert 'API section is not found' in str(exc.value)
    finally:
        os.remove(path)


def test_read_ini_valid_file_returns_config():
    with tempfile.NamedTemporaryFile('w', suffix='.ini', delete=False) as fh:
        fh.write(
            '[API]\n'
            'USERNAME = admin\n'
            'PASSWORD = secret\n'
            'PROTOCOL = https\n'
            'ENDPOINT = 10.0.0.1:7050\n'
            'SECRET_KEY = abc\n'
            'VERIFY_CERTIFICATE = no\n'
        )
        path = fh.name
    try:
        config = Ini.read_ini(path)
        assert config['USERNAME'] == 'admin'
        assert config['ENDPOINT'] == '10.0.0.1:7050'
        assert config['VERIFY_CERTIFICATE'] is False
    finally:
        os.remove(path)


# ── base.token.Token.get_token ───────────────────────────────────────────

class _FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


def test_get_token_bad_status_raises_not_exits(monkeypatch):
    monkeypatch.setattr(token_module.session, 'post',
                        lambda *a, **k: _FakeResponse(401, '{}'))
    with pytest.raises(Exception) as exc:
        Token.get_token('u', 'p', 'https', 'host')
    assert not isinstance(exc.value, SystemExit)
    assert 'invalid credentials' in str(exc.value)


def test_get_token_no_token_in_response_raises(monkeypatch):
    monkeypatch.setattr(token_module.session, 'post',
                        lambda *a, **k: _FakeResponse(200, '{"foo": 1}'))
    with pytest.raises(Exception) as exc:
        Token.get_token('u', 'p', 'https', 'host')
    assert 'did not receive a token' in str(exc.value)


def test_get_token_connection_error_raises_not_exits(monkeypatch):
    def _boom(*a, **k):
        raise requests.exceptions.ConnectionError('no route to host')
    monkeypatch.setattr(token_module.session, 'post', _boom)
    with pytest.raises(Exception) as exc:
        Token.get_token('u', 'p', 'https', 'host')
    assert not isinstance(exc.value, SystemExit)
    assert 'trouble getting my token' in str(exc.value)


# ── app.validate_home_directory (before_request) ─────────────────────────

def test_before_request_missing_ini_raises(slurm_app, monkeypatch):
    # the slurm_app fixture mocks os.path.isfile to True for its whole lifetime;
    # force the missing-file branch for this check.
    monkeypatch.setattr(os.path, 'isfile', lambda p: False)
    slurm_app.TOKEN_FILE = '/tmp/.luna-token.dat'
    slurm_app.INI_FILE = '/nonexistent/luna.ini'
    with slurm_app.app.test_request_context('/json/configuration/nodes'):
        with pytest.raises(Exception) as exc:
            slurm_app.validate_home_directory()
    assert 'Not Found' in str(exc.value)


def test_before_request_bad_home_raises(slurm_app):
    slurm_app.TOKEN_FILE = {'error': 'the home directory is broken'}
    with slurm_app.app.test_request_context('/json/configuration/nodes'):
        with pytest.raises(Exception) as exc:
            slurm_app.validate_home_directory()
    assert 'home directory is broken' in str(exc.value)


def test_wrap_errors_formats_message(slurm_app):
    with slurm_app.app.test_request_context('/'):
        response, status = slurm_app.wrap_errors(Exception('boom detail'))
    assert status == 500
    assert response.get_json()['message'] == 'boom detail'
