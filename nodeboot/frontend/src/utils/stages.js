// Boot Overview / Boot Progress numbers. The stage counts come from the backend's
// group.overview and group.funnel, computed with the same tables as `luna boot status`
// (luna2-cli 2.2) so the web view and the CLI agree - including the CLI's habit of
// counting install.discovered and install.error under config, which is left as is.
// failed/unknown stay ours, from failedReasons, because the Nodes list behind those
// counts is keyed on the same reasons.

export const FUNNEL_STAGES = [
  { key: 'discovered', hint: 'iPXE asked for a boot' },
  { key: 'rendered', hint: 'installer handed out' },
  { key: 'prepared', hint: 'scripts, prescript, BMC, partscript' },
  { key: 'downloaded', hint: 'image fetched' },
  { key: 'unpacked', hint: 'unpack, or the lpart part phase' },
  { key: 'configured', hint: 'setnet, secrets, postscript, roles, profiles' },
  { key: 'booted', hint: 'up and reported in' },
]

function countReason(group, reason) {
  return Object.values(group.failedReasons || {}).filter((r) => r === reason).length
}

export function overviewOf(group) {
  const { ipxe, download, unpack, config, done } = group.overview
  return {
    ipxe, download, unpack, config, done,
    failed: countReason(group, 'error'),
    unknown: countReason(group, 'not_started'),
    total: group.total,
    booting: group.booting,
  }
}

// Sum of groups, so the "all nodes" view and a single row share one code path.
export function funnelOf(groups) {
  let total = 0, booted = 0, booting = 0, failed = 0
  const reached = Object.fromEntries(FUNNEL_STAGES.map(({ key }) => [key, 0]))
  for (const g of groups) {
    total += g.total
    booted += g.booted
    booting += g.booting
    failed += g.failed
    for (const key in reached) reached[key] += g.funnel[key]
  }
  return { total, booted, booting, failed, reached }
}

export function pctOf(count, total) {
  return total ? Math.round((count / total) * 100) : 0
}
