"""
conftest.py — pytest fixtures for the TrinityX OOD Slurm app.

Package strategy
----------------
trinityx_config_blocks    — real package (installed from GitLab repo)
trinityx_config_slurm     — real package (installed from GitLab repo)
slurmlint                 — stubbed (not available; lint always passes)
base.config               — stubbed (avoids /trinity/local/… ini file)
helpers                   — stubbed (avoids live Luna daemon call)

If either trinityx package is missing the suite will still run using
lightweight fallback stubs so CI without the GitLab packages stays green.

Install the real packages once with:
  pip install -e /path/to/trinityx-config-blocks
  pip install -e /path/to/trinityx-config-slurm
"""

import sys
import os
import types
import tempfile
import pytest

# ── Make the slurm/ directory importable ─────────────────────────────────
SLURM_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(SLURM_DIR))


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  trinityx_config_blocks — real if available, fallback stub otherwise  ║
# ╚══════════════════════════════════════════════════════════════════════╝

try:
    import trinityx_config_blocks  # noqa — just verify importable
    _CONFIG_BLOCKS_REAL = True
except ImportError:
    _CONFIG_BLOCKS_REAL = False

if not _CONFIG_BLOCKS_REAL:
    import re as _re

    class _ConfigFileFallback:
        """Fallback ConfigFile stub when real package unavailable."""
        BLOCK_RE = _re.compile(
            r'(####\s+(?P<name>\S+)\s+Managed block start\s+####)'
            r'(?P<content>.*?)'
            r'(####\s+(?P=name)\s+Managed block end\s+####)',
            _re.DOTALL
        )

        def __init__(self, path):
            self._path = path
            self._raw = ""
            self._blocks = {}
            if path and os.path.exists(path):
                with open(path) as fh:
                    self._raw = fh.read()
                for m in self.BLOCK_RE.finditer(self._raw):
                    self._blocks[m.group('name')] = m.group('content')

        @classmethod
        def read(cls, path):
            return cls(path)

        def ismanaged(self, name):
            return name in self._blocks

        def get_managed_block(self, name):
            return self._blocks.get(name, "")

        def set_managed_block(self, name, content):
            self._blocks[name] = content

        def write(self, path):
            result = self._raw
            for name, content in self._blocks.items():
                pattern = (
                    rf'(####\s+{_re.escape(name)}\s+Managed block start\s+####)'
                    rf'(.*?)'
                    rf'(####\s+{_re.escape(name)}\s+Managed block end\s+####)'
                )
                result = _re.sub(pattern, rf'\g<1>{content}\g<3>', result, flags=_re.DOTALL)
            with open(path, 'w') as fh:
                fh.write(result)
            self._raw = result

        def dump(self):
            return self._raw

    _mod = types.ModuleType('trinityx_config_blocks')
    _mod.ConfigFile = _ConfigFileFallback
    sys.modules['trinityx_config_blocks'] = _mod


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  trinityx_config_slurm — real if available, fallback stub otherwise   ║
# ╚══════════════════════════════════════════════════════════════════════╝

try:
    import trinityx_config_slurm  # noqa
    _CONFIG_SLURM_REAL = True
except ImportError:
    _CONFIG_SLURM_REAL = False

if not _CONFIG_SLURM_REAL:
    import re as _re2

    class _SlurmConfigFallback:
        def __init__(self, entries):
            self._entries = entries  # list of dicts

        @classmethod
        def parse(cls, text):
            entries = []
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                pairs = {}
                for m in _re2.finditer(r'(\w+)=(\S+)', line):
                    pairs[m.group(1)] = m.group(2)
                if pairs:
                    entries.append(pairs)
            return cls(entries)

        def object_aslist(self, entry=None):
            return [e for e in self._entries if not entry or entry in e]

        def object(self, multiple=False):
            result = {}
            for e in self._entries:
                if e:
                    k, v = next(iter(e.items()))
                    result[f"{k}={v}"] = ' '.join(f"{ki}={vi}" for ki, vi in e.items())
            return result

        def comment(self, name=None, multiple=False):
            return {}

    class _GenerateFallback:
        def all_configs(self, nodes, configs, manager):
            return True

    _pkg = types.ModuleType('trinityx_config_slurm')
    _pkg.SlurmConfig   = _SlurmConfigFallback
    _pkg.SlurmEntry    = object
    _pkg.SlurmProperty = object
    _pkg.Generate      = _GenerateFallback
    _utils = types.ModuleType('trinityx_config_slurm.utils')
    _hl    = types.ModuleType('trinityx_config_slurm.utils.hostlist')
    try:
        import hostlist as _sys_hl
        _hl.compress = lambda s: _sys_hl.collect_hostlist(s.split(',')) if s else s
        _hl.expand   = lambda s: ','.join(_sys_hl.expand_hostlist(s))
    except ImportError:
        _hl.compress = lambda s: s
        _hl.expand   = lambda s: s
    _pkg.utils = _utils
    _utils.hostlist = _hl
    sys.modules['trinityx_config_slurm']               = _pkg
    sys.modules['trinityx_config_slurm.utils']         = _utils
    sys.modules['trinityx_config_slurm.utils.hostlist'] = _hl


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  slurmlint — always stubbed (not available anywhere)                  ║
# ╚══════════════════════════════════════════════════════════════════════╝

_sl     = types.ModuleType('slurmlint')
_sl_l   = types.ModuleType('slurmlint.linter')
_sl_l.lint = lambda text: {"errors": []}
_sl.linter = _sl_l
sys.modules['slurmlint']        = _sl
sys.modules['slurmlint.linter'] = _sl_l


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  helpers — stubbed (no live Luna daemon needed)                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

_helpers = types.ModuleType('helpers')
_helpers.get_luna_nodes = lambda: {}
_helpers.managed_by_ood = lambda: False
sys.modules['helpers'] = _helpers


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  base.config — stubbed to point at temp files                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

_MANAGED_BLOCK_TEMPLATE = (
    "#### Defaults Managed block start ####\n"
    "#### Defaults Managed block end   ####\n\n"
    "#### TrinityX Managed block start ####\n"
    "#### TrinityX Managed block end   ####\n"
)


def _install_base_config_stub(tmp_dir):
    files = {k: os.path.join(tmp_dir, v) for k, v in {
        'nodes':         'slurm-nodes.conf',
        'partitions':    'slurm-partitions.conf',
        'gres':          'gres.conf',
        'nodes_bkp':     'slurm-nodes.conf.bkp',
        'partitions_bkp':'slurm-partitions.conf.bkp',
        'gres_bkp':      'gres.conf.bkp',
    }.items()}
    for path in files.values():
        with open(path, 'w') as fh:
            fh.write(_MANAGED_BLOCK_TEMPLATE)

    _base     = types.ModuleType('base')
    _bcfg     = types.ModuleType('base.config')
    _bini     = types.ModuleType('base.ini')
    _btok     = types.ModuleType('base.token')

    _bcfg.MANAGER_NAME       = 'TrinityX'
    _bcfg.MANAGER_NAME_OOD   = 'TrinityX-OOD'
    _bcfg.MANAGED_PROPERTIES = [
        'Boards','SocketsPerBoard','CoresPerSocket','ThreadsPerCore',
        'RealMemory','TmpDisk','CpuBind','Gres','State'
    ]
    _bcfg.get_configs            = lambda: {'LUNA': {}, 'APP': {}, 'ENV': {}}
    _bcfg.get_slurm_files        = lambda: {k: files[k] for k in ('nodes','partitions','gres')}
    _bcfg.get_slurm_backup_files = lambda: {k: files[k+'_bkp'] for k in ('nodes','partitions','gres')}

    _base.config = _bcfg
    sys.modules.update({'base': _base, 'base.config': _bcfg,
                        'base.ini': _bini, 'base.token': _btok})
    return files


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  pytest FIXTURES                                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

@pytest.fixture(scope='session')
def tmp_slurm_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture(scope='session')
def slurm_files(tmp_slurm_dir):
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
