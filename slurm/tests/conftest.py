"""
conftest.py — pytest fixtures and stubs for the TrinityX OOD Slurm app.

All unavailable private packages (trinityx_config_blocks,
trinityx_config_slurm, slurmlint) are replaced with minimal stubs so
the test suite runs standalone — no Slurm, no Flask prod config,
no GitLab package registry needed.
"""

import sys
import os
import types
import tempfile
import pytest

# ── Make the slurm/ directory importable ────────────────────────────────
SLURM_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(SLURM_DIR))


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STUB: trinityx_config_blocks                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

class _ConfigFileMock:
    """
    Minimal stand-in for trinityx_config_blocks.ConfigFile.
    Reads a real file on disk so we can test with temp-file fixtures,
    but stubs out every method the app calls.
    """
    def __init__(self, path):
        self._path = path
        self._blocks = {}   # block_name -> content str
        self._raw = ""
        if path and os.path.exists(path):
            with open(path) as fh:
                self._raw = fh.read()
            self._parse_blocks()

    def _parse_blocks(self):
        import re
        for m in re.finditer(
            r'####\s+(\S+)\s+Managed block start\s+####(.*?)####\s+\1\s+Managed block end\s+####',
            self._raw, re.DOTALL
        ):
            self._blocks[m.group(1)] = m.group(2)

    # ── API surface used by app.py ──────────────────────────────────────
    @classmethod
    def read(cls, path):
        return cls(path)

    def ismanaged(self, block_name):
        return block_name in self._blocks

    def get_managed_block(self, block_name):
        return self._blocks.get(block_name, "")

    def set_managed_block(self, block_name, content):
        self._blocks[block_name] = content

    def write(self, path):
        # Re-assemble the file with updated blocks
        import re
        result = self._raw
        for name, content in self._blocks.items():
            pattern = (
                rf'(####\s+{re.escape(name)}\s+Managed block start\s+####)'
                rf'(.*?)'
                rf'(####\s+{re.escape(name)}\s+Managed block end\s+####)'
            )
            replacement = rf'\g<1>{content}\g<3>'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
        with open(path, 'w') as fh:
            fh.write(result)
        self._path = path
        self._raw = result

    def dump(self):
        return self._raw


def _install_config_blocks_stub():
    mod = types.ModuleType('trinityx_config_blocks')
    mod.ConfigFile = _ConfigFileMock
    sys.modules['trinityx_config_blocks'] = mod

_install_config_blocks_stub()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STUB: trinityx_config_slurm                                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

class _SlurmConfigMock:
    """
    Minimal SlurmConfig — just enough to let app.py parse the key=value
    lines it cares about (NodeName=, PartitionName=, HWPresetName=,
    GRESPresetName=, NodeSet=).
    """
    def __init__(self, entries):
        # entries: list of dicts, each dict is one parsed stanza
        self._entries = entries

    @classmethod
    def parse(cls, text):
        import re
        entries = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            pairs = {}
            for m in re.finditer(r'(\w+)=(\S+)', line):
                pairs[m.group(1)] = m.group(2)
            if pairs:
                entries.append(pairs)
        return cls(entries)

    def object_aslist(self, entry):
        return [e for e in self._entries if entry in e]

    def object(self, multiple=True):
        """Return dict keyed by first key=value as 'KEY=VAL' -> rest-of-line"""
        result = {}
        for e in self._entries:
            if e:
                key = list(e.keys())[0]
                val = list(e.values())[0]
                result[f"{key}={val}"] = ' '.join(f"{k}={v}" for k, v in e.items())
        return result

    def comment(self, name=None):
        """
        Returns comment metadata dict.  We return an empty dict here —
        tests that need specific comment data set it up via file fixtures.
        """
        return {}


class _GenerateMock:
    def all_configs(self, nodes, configs, manager):
        return True   # always succeed in tests


def _install_config_slurm_stub():
    pkg = types.ModuleType('trinityx_config_slurm')
    pkg.SlurmConfig  = _SlurmConfigMock
    pkg.SlurmEntry   = object
    pkg.SlurmProperty = object
    pkg.Generate     = _GenerateMock

    utils = types.ModuleType('trinityx_config_slurm.utils')
    hostlist = types.ModuleType('trinityx_config_slurm.utils.hostlist')

    # Real hostlist logic using the system python-hostlist package
    try:
        import hostlist as _hl
        hostlist.compress = lambda s: _hl.collect_hostlist(s.split(',')) if s else s
        hostlist.expand   = lambda s: ','.join(_hl.expand_hostlist(s))
    except ImportError:
        # Fallback: identity functions (no compression/expansion)
        hostlist.compress = lambda s: s
        hostlist.expand   = lambda s: s

    pkg.utils = utils
    utils.hostlist = hostlist
    sys.modules['trinityx_config_slurm'] = pkg
    sys.modules['trinityx_config_slurm.utils'] = utils
    sys.modules['trinityx_config_slurm.utils.hostlist'] = hostlist

_install_config_slurm_stub()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STUB: slurmlint                                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def _install_slurmlint_stub():
    slurmlint     = types.ModuleType('slurmlint')
    linter        = types.ModuleType('slurmlint.linter')
    linter.lint   = lambda text: {"errors": []}   # always valid
    slurmlint.linter = linter
    sys.modules['slurmlint']        = slurmlint
    sys.modules['slurmlint.linter'] = linter

_install_slurmlint_stub()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STUB: base.config  (avoids reading /trinity/local/… ini file)       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def _install_base_config_stub(tmp_dir):
    nodes_file = os.path.join(tmp_dir, 'slurm-nodes.conf')
    parts_file = os.path.join(tmp_dir, 'slurm-partitions.conf')
    gres_file  = os.path.join(tmp_dir, 'gres.conf')
    nodes_bkp  = nodes_file + '.bkp'
    parts_bkp  = parts_file + '.bkp'
    gres_bkp   = gres_file  + '.bkp'

    _managed_block_template = (
        "#### Defaults Managed block start ####\n"
        "#### Defaults Managed block end   ####\n\n"
        "#### TrinityX Managed block start ####\n"
        "#### TrinityX Managed block end   ####\n"
    )
    for path in [nodes_file, parts_file, gres_file,
                 nodes_bkp,  parts_bkp,  gres_bkp]:
        with open(path, 'w') as fh:
            fh.write(_managed_block_template)

    base_pkg    = types.ModuleType('base')
    base_config = types.ModuleType('base.config')
    base_ini    = types.ModuleType('base.ini')
    base_token  = types.ModuleType('base.token')

    base_config.MANAGER_NAME      = 'TrinityX'
    base_config.MANAGER_NAME_OOD  = 'TrinityX-OOD'
    base_config.MANAGED_PROPERTIES = [
        'Boards','SocketsPerBoard','CoresPerSocket','ThreadsPerCore',
        'RealMemory','TmpDisk','CpuBind','Gres','State'
    ]
    base_config.get_configs        = lambda: {'LUNA': {}, 'APP': {}, 'ENV': {}}
    base_config.get_slurm_files    = lambda: {
        'nodes': nodes_file, 'partitions': parts_file, 'gres': gres_file
    }
    base_config.get_slurm_backup_files = lambda: {
        'nodes': nodes_bkp, 'partitions': parts_bkp, 'gres': gres_bkp
    }

    base_pkg.config = base_config
    sys.modules['base']        = base_pkg
    sys.modules['base.config'] = base_config
    sys.modules['base.ini']    = base_ini
    sys.modules['base.token']  = base_token

    return {
        'nodes': nodes_file, 'partitions': parts_file, 'gres': gres_file,
        'nodes_bkp': nodes_bkp, 'partitions_bkp': parts_bkp, 'gres_bkp': gres_bkp,
    }


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STUB: helpers                                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

def _install_helpers_stub():
    helpers = types.ModuleType('helpers')
    helpers.get_luna_nodes  = lambda: {}
    helpers.managed_by_ood  = lambda: False
    sys.modules['helpers'] = helpers

_install_helpers_stub()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  pytest FIXTURES                                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

@pytest.fixture(scope='session')
def tmp_slurm_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture(scope='session')
def slurm_files(tmp_slurm_dir):
    """
    Install the base.config stub pointing at temp files and return
    the file-path dict.  session-scoped so the app module is only
    imported once.
    """
    return _install_base_config_stub(tmp_slurm_dir)


@pytest.fixture(scope='session')
def slurm_app(slurm_files):
    """Import the slurm app module and configure it for testing."""
    import unittest.mock as mock
    with mock.patch('os.path.isfile', return_value=True), \
         mock.patch('os.access',      return_value=True):
        import app as _mod
        _mod.app.config['TESTING'] = True
        _mod.SLURM_FILES        = slurm_files
        _mod.SLURM_BACKUP_FILES = {
            'nodes':      slurm_files['nodes_bkp'],
            'partitions': slurm_files['partitions_bkp'],
            'gres':       slurm_files['gres_bkp'],
        }
        yield _mod


@pytest.fixture(scope='session')
def client(slurm_app):
    """Flask test client — before_request INI check cleared for tests."""
    slurm_app.app.config['TESTING'] = True
    slurm_app.app.before_request_funcs[None] = []
    with slurm_app.app.test_client() as c:
        yield c
