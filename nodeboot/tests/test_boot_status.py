"""
test_boot_status.py — the numbers behind Node Boot's three panels.

Everything here is pure: classify_group(), build_images() and boot_view() are
fed node records and monitor rows as the daemon would return them. The stage
tables come from luna2-cli, so these tests also pin that the page agrees with
`luna boot status -l` on the same input.
"""

from datetime import datetime, timedelta


def _stamp(minutes_ago):
    return (datetime.utcnow() - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')


# ── stage classification ─────────────────────────────────────────────────

def test_every_ladder_step_is_placed(app_module):
    # every step the CLI's ladder knows lands in a phase or in booted -- never
    # in failedReasons. This is the class of bug a hand-written state list had:
    # lpart.pre/part/post, mounts, profiles and sanitized were unknown to it
    # and installing nodes showed as "not booting".
    ladder = [f'install.{step}' for _name, steps, _pct in app_module.Boot.BOOT_STAGES for step in steps]
    placed = app_module.classify_group(ladder, dict(zip(ladder, ladder)))
    assert placed['failed'] == 0, placed['failedReasons']
    assert placed['booted'] + placed['booting'] == len(ladder)


def test_single_states(app_module):
    one = lambda state: app_module.classify_group(['t'], {'t': state})
    assert one('booted')['booted'] == 1  # legacy pre-rewrite value still counts
    assert one('install.lpart.pre')['phase1'] == 1
    assert one('install.download')['phase2'] == 1
    assert one('install.lpart.part')['phase3'] == 1
    assert one('install.mounts')['phase3'] == 1 and one('install.profiles')['phase3'] == 1
    assert one('install.success')['phase3'] == 1  # installed, not yet booted: not done
    assert one('install.sanitized')['booted'] == 1
    assert one('install.fatal')['failedReasons'] == {'t': 'parked'}
    assert one('install.error')['failedReasons'] == {'t': 'error'}
    assert one(None)['failedReasons'] == {'t': 'not_started'}


def test_overview_columns_follow_the_cli_order(app_module):
    assert list(app_module.boot_overview([])) == ['unknown', 'ipxe', 'download', 'unpack', 'config', 'parked', 'done']


# ── per-group counts ─────────────────────────────────────────────────────

def test_same_group_two_phases_not_merged(app_module, node, overview):
    # Two nodes, same image, same group, one in phase1 one in phase2 -- not
    # merged with each other, and neither is "failed".
    nodes = {'test01': node('compute01'), 'test02': node('compute01')}
    images = app_module.build_images(nodes, {'test01': 'install.discovered', 'test02': 'install.downloaded'})
    assert len(images) == 1
    img = images[0]
    assert img['name'] == 'img'
    assert len(img['groups']) == 1
    g = img['groups'][0]
    assert g == {'name': 'compute01', 'network': 'cluster', 'total': 2, 'booted': 0,
                 'booting': 2, 'phase1': 1, 'phase2': 1, 'phase3': 0,
                 'failed': 0, 'failedNodes': [], 'failedReasons': {},
                 'overview': overview(ipxe=1, download=1),
                 'funnel': {'discovered': 2, 'rendered': 1, 'prepared': 1, 'downloaded': 0,
                            'unpacked': 0, 'configured': 0, 'booted': 0},
                 'progress': None}, g


def test_two_groups_stay_separate(app_module, node):
    nodes = {'test01': node('compute01'), 'test02': node('compute02')}
    images = app_module.build_images(nodes, {'test01': 'install.booted', 'test02': 'install.booted'})
    assert len(images[0]['groups']) == 2
    by_name = {g['name']: g for g in images[0]['groups']}
    assert by_name['compute01']['booted'] == 1 and by_name['compute02']['booted'] == 1


def test_phase_boundaries_overview_and_funnel(app_module, node, overview):
    # phase boundaries: discovered->downloaded is phase1, downloaded->unpack is
    # phase2, unpack->booted is phase3 -- exactly the 3 states asked for.
    nodes = {n: node('compute01') for n in ('test01', 'test02', 'test03', 'test04')}
    images = app_module.build_images(nodes, {
        'test01': 'install.discovered', 'test02': 'install.downloaded',
        'test03': 'install.unpack', 'test04': 'install.booted',
    })
    g = images[0]['groups'][0]
    assert (g['phase1'], g['phase2'], g['phase3'], g['booted']) == (1, 1, 1, 1), g
    # overview/funnel use the CLI's own tables, so they match `luna boot status`:
    # discovered and rendered are the ipxe phase, and a milestone counts as
    # passed only once the node is in the stage after it (install.downloaded
    # has not passed 'downloaded', install.unpack has).
    assert g['overview'] == overview(ipxe=1, download=1, unpack=1, done=1), g['overview']
    assert g['funnel'] == {'discovered': 4, 'rendered': 3, 'prepared': 3, 'downloaded': 2,
                           'unpacked': 1, 'configured': 1, 'booted': 1}, g['funnel']


def test_early_node_beside_booted_peers_is_not_failed(app_module, node):
    # a node still early in the pipeline while a sibling has already booted is
    # NORMAL, not "failed" -- the regression this test exists to catch (an
    # earlier version flagged it "stuck" purely for being >=25 points behind a
    # booted peer, which is true of almost every mid-pipeline node the instant
    # anyone in its group finishes).
    nodes = {n: node('compute01') for n in ('test01', 'test02', 'test03')}
    images = app_module.build_images(nodes, {'test01': 'install.booted', 'test02': 'install.booted',
                                             'test03': 'install.discovered'})
    g = images[0]['groups'][0]
    assert g['failed'] == 0, g
    assert g['booted'] == 2 and g['phase1'] == 1


def test_install_error_is_failed(app_module, node):
    nodes = {n: node('compute01') for n in ('test01', 'test02', 'test03')}
    images = app_module.build_images(nodes, {'test01': 'install.error', 'test02': 'install.booted',
                                             'test03': 'install.discovered'})
    g = images[0]['groups'][0]
    assert g['booted'] == 1 and g['failed'] == 1
    assert g['failedReasons'] == {'test01': 'error'}


def test_missing_monitor_entry_is_not_started(app_module, node):
    # a node with no monitor entry at all (never reached install.discovered)
    # counts as not booting, not as an early-phase booting node
    nodes = {n: node('compute01') for n in ('test01', 'test02')}
    images = app_module.build_images(nodes, {'test01': 'install.discovered'})  # test02 has no entry
    g = images[0]['groups'][0]
    assert g['booting'] == 1 and g['phase1'] == 1
    assert g['failed'] == 1 and g['failedReasons'] == {'test02': 'not_started'}
    # a node with no state is 'unknown' in the overview and reaches no milestone
    assert g['overview']['unknown'] == 1 and g['overview']['ipxe'] == 1, g['overview']
    assert g['funnel']['discovered'] == 1 and g['funnel']['booted'] == 0, g['funnel']


# ── images and groups without nodes ──────────────────────────────────────

def test_unused_image_is_listed_with_no_groups(app_module, node):
    # an osimage with zero nodes still gets listed (empty groups) when we know
    # about it from Luna's own osimage list; a group with zero nodes still
    # never gets synthesized, since groups only exist as a byproduct of nodes
    nodes = {'test01': node('rack01')}
    images = app_module.build_images(nodes, {'test01': 'install.booted'},
                                     all_osimage_names=['img', 'unused-image'])
    by_name = {i['name']: i for i in images}
    assert set(by_name) == {'img', 'unused-image'}, by_name
    assert by_name['unused-image']['groups'] == []


def test_unused_groups_are_named_under_their_image(app_module, node):
    # groups with no nodes are named under their own osimage's unusedGroups,
    # including an osimage nothing else references; groups with nodes are not
    nodes = {'test01': node('rack01')}
    images = app_module.build_images(nodes, {'test01': 'install.booted'}, all_osimage_names=['img'],
                                     all_groups={'rack01': 'img', 'rack02': 'img', 'spare': 'other-image'})
    by_name = {i['name']: i for i in images}
    assert by_name['img']['unusedGroups'] == ['rack02'], by_name
    assert [g['name'] for g in by_name['img']['groups']] == ['rack01']
    assert by_name['other-image'] == {'id': 'other-image', 'name': 'other-image',
                                      'groups': [], 'unusedGroups': ['spare']}, by_name


# ── the progress block: the CLI's own luna boot status -l ────────────────

def _cohort(node):
    # cohort anchored on the in-flight node, a parked node is not in flight,
    # sanitized counts as done, a silent node is stuck
    nodes = {n: node('compute01') for n in ('test01', 'test02', 'test03', 'test04', 'test05')}
    monitor = {
        'test01': {'state': 'install.booted', 'status': '200', 'updated': _stamp(3)},
        'test02': {'state': 'install.unpack', 'status': '200', 'updated': _stamp(2)},
        'test03': {'state': 'install.degraded', 'status': '200', 'updated': _stamp(95)},
        'test04': {'state': 'install.sanitized', 'status': '200', 'updated': _stamp(40)},
        'test05': {'state': 'install.discovered', 'status': '200', 'updated': _stamp(120)},
    }
    return nodes, monitor


def test_progress_block(app_module, node, overview):
    nodes, monitor = _cohort(node)
    states = {name: row['state'] for name, row in monitor.items()}
    g = app_module.build_images(nodes, states, monitor=monitor)[0]['groups'][0]
    assert g['overview'] == overview(ipxe=1, unpack=1, parked=1, done=2), g['overview']
    p = g['progress']
    assert p['nodes'] == 5 and p['anchored'] is True, p
    assert [s['node'] for s in p['stuck']] == ['test05'], p['stuck']
    assert {m['milestone']: m['nodes'] for m in p['milestones']}['booted'] == 1
    by_node = {row['node']: row for row in p['notBooted']}
    assert set(by_node) == {'test02', 'test03', 'test04', 'test05'}, by_node
    assert by_node['test02']['condition'] == '' and by_node['test02']['stage'] == 'unpack'
    assert by_node['test03']['condition'] == 'parked' and by_node['test03']['step'] == 'degraded'
    assert by_node['test04']['condition'] == 'sanitized'
    assert by_node['test05']['condition'] == 'stuck' and by_node['test05']['minutes'] >= 120


def test_operator_actions(app_module, node):
    # every stopped state the installer can report carries its operator action;
    # a node that is merely slow or mid-install carries none
    nodes, monitor = _cohort(node)
    by_node = {row['node']: row for row in app_module.boot_view(monitor, nodes, sorted(nodes))['notBooted']}
    assert by_node['test03']['action'] == 'replace the disk, reinstall with install_mode full'
    assert by_node['test04']['action'] == 'none, or reinstall'
    assert by_node['test02']['action'] == '' and by_node['test05']['action'] == ''
    for step in ('degraded', 'refused', 'fatal', 'sanitized', 'error'):
        assert app_module.OPERATOR_ACTIONS[step], step


def test_installer_500_is_failed(app_module, node):
    # a 500 from the installer is what the daemon classes as failed
    nodes, monitor = _cohort(node)
    monitor['test02']['status'] = '500'
    rows = app_module.boot_view(monitor, nodes, ['test02'])['notBooted']
    assert {r['node']: r['condition'] for r in rows} == {'test02': 'failed'}


def test_no_monitor_rows_gives_no_block(app_module, node):
    # no monitor rows at all: no cohort, no block -- the CLI's None, not a crash
    nodes, _monitor = _cohort(node)
    assert app_module.boot_view({}, nodes, list(nodes)) is None
