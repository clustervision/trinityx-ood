// Boot Overview counts come from the backend's group.overview and the Boot Progress /
// Not Booted blocks from group.progress and data.progress, all computed with the CLI's
// own code so the web view and `luna boot status -l` agree. Nothing here recounts.
// failed/unknown stay ours, from failedReasons, because the Nodes list behind those
// counts is keyed on the same reasons.

function countReason(group, reason) {
  return Object.values(group.failedReasons || {}).filter((r) => r === reason).length
}

export function overviewOf(group) {
  return {
    ...group.overview,
    failed: countReason(group, 'error'),
    unknown: countReason(group, 'not_started'),
    total: group.total,
    booting: group.booting,
  }
}

export function pctOf(count, total) {
  return total ? Math.round((count / total) * 100) : 0
}

// Minutes the way the CLI prints them: 12m, 1h35m, '-' when nothing was reported.
export function formatAge(minutes) {
  if (minutes === null || minutes === undefined) return '-'
  if (minutes < 60) return `${minutes}m`
  return `${Math.floor(minutes / 60)}h${String(minutes % 60).padStart(2, '0')}m`
}
