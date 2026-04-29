const IPV4_RE =
  /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})$/

export function parseIpv4String(s) {
  if (s == null) return null
  const t = String(s).trim().split(/\s+/)[0]
  if (!IPV4_RE.test(t)) return null
  const parts = t.split('.').map(Number)
  return ((parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]) >>> 0
}

export function formatIpv4(n) {
  if (n == null || !Number.isFinite(n)) return ''
  const x = n >>> 0
  return [x >>> 24, (x >>> 16) & 0xff, (x >>> 8) & 0xff, x & 0xff].join('.')
}

function network24Base(ipNum) {
  return (ipNum >>> 0) & 0xffffff00
}

function collectSubnetBase(networkName, formInterfaces, inventoryRecords, excludeNodeName) {
  const net = String(networkName || '').trim()
  if (!net) return null
  for (const r of inventoryRecords) {
    if (excludeNodeName && r.nodeName === excludeNodeName) continue
    if (String(r.network || '').trim() === net && r.ipNum != null) {
      return network24Base(r.ipNum)
    }
  }
  for (const iface of formInterfaces) {
    if (String(iface.network || '').trim() !== net) continue
    const ipNum = parseIpv4String(iface.ipaddress)
    if (ipNum != null) return network24Base(ipNum)
  }
  return null
}

function buildUsedSet(inventoryRecords, excludeNodeName, formInterfaces) {
  const used = new Set()
  for (const r of inventoryRecords) {
    if (excludeNodeName && r.nodeName === excludeNodeName) continue
    if (r.ipNum != null) used.add(r.ipNum)
  }
  for (const iface of formInterfaces) {
    const ipNum = parseIpv4String(iface.ipaddress)
    if (ipNum != null) used.add(ipNum)
  }
  return used
}

/**
 * Picks the lowest free host IPv4 in the /24 inferred from existing assignments on the same network.
 * @returns {{ ok: true, ip: string } | { ok: false, reason: 'network' | 'subnet' | 'full' }}
 */
export function suggestNextFreeIpv424({
  networkName,
  formInterfaces,
  inventoryRecords,
  excludeNodeName,
}) {
  const net = String(networkName || '').trim()
  if (!net) return { ok: false, reason: 'network' }

  const base = collectSubnetBase(net, formInterfaces, inventoryRecords, excludeNodeName || '')
  if (base == null) return { ok: false, reason: 'subnet' }

  const used = buildUsedSet(inventoryRecords, excludeNodeName || '', formInterfaces)

  for (let host = 1; host <= 254; host++) {
    const cand = (base >>> 0) + host
    if (!used.has(cand)) return { ok: true, ip: formatIpv4(cand) }
  }
  return { ok: false, reason: 'full' }
}
