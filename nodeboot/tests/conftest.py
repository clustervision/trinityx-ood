"""
conftest.py — pytest fixtures for the TrinityX OOD Node Boot app.

The app's pure logic (stage classification, per-group counts, the progress
block) is exercised directly; no daemon, no luna.ini, no token. The module
imports luna.boot from luna2-cli, which has to be installed where the tests run,
as it is on a controller: the suite skips rather than fails without it.
"""

import os
import sys

import pytest

# ── Make the nodeboot/ directory importable ──────────────────────────────
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, APP_DIR)


@pytest.fixture(scope='session')
def app_module():
    """The application module, with the CLI tables it derives everything from."""
    pytest.importorskip('luna.boot')
    import app
    return app


@pytest.fixture
def node():
    """A node record as /config/node returns it, reduced to what build_images reads."""
    def make(group, osimage='img', network='cluster'):
        return {'osimage': osimage, 'group': group, 'provision_method': 'torrent',
                'provision_interface': 'BOOTIF',
                'interfaces': [{'interface': 'BOOTIF', 'network': network}]}
    return make


@pytest.fixture
def overview(app_module):
    """An expected overview row: the CLI's columns, all zero, with overrides. The
    columns are whatever the installed CLI's BOOT_PHASES says, so the expectation
    is built from that table rather than spelled out."""
    def make(**counts):
        return {**app_module.boot_overview([]), **counts}
    return make
