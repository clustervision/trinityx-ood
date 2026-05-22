export function formatIpv4Typing(input: string): string {
  const raw = String(input ?? '')
  const trailingDot = raw.endsWith('.')
  const normalized = raw.replace(/[^0-9.]/g, '')

  if (!normalized) return ''

  if (normalized.includes('.')) {
    const parts = normalized.split('.').slice(0, 4)
    const octets = parts.map((part) => clampOctetDigits(part.replace(/\D/g, '').slice(0, 3)))
    while (octets.length > 1 && octets[octets.length - 1] === '' && !trailingDot) {
      octets.pop()
    }
    return octets.length ? octets.join('.') : ''
  }

  const digits = normalized.replace(/\D/g, '').slice(0, 12)
  if (!digits) return ''

  const octets: string[] = []
  for (let i = 0; i < digits.length && octets.length < 4; ) {
    const rest = digits.length - i
    const take = rest <= 3 ? rest : 3
    octets.push(clampOctetDigits(digits.slice(i, i + take)))
    i += take
  }
  return octets.join('.')
}

function clampOctetDigits(digits: string): string {
  if (!digits) return ''
  return String(Math.min(parseInt(digits, 10), 255))
}

const IPV4_OCTET = '(?:25[0-5]|2[0-4]\\d|[01]?\\d\\d?)'
const IPV4_FULL = new RegExp(`^${IPV4_OCTET}\\.${IPV4_OCTET}\\.${IPV4_OCTET}\\.${IPV4_OCTET}$`)

/** True only for four dotted octets (0–255 each). */
export function isValidIpv4(value: string): boolean {
  return IPV4_FULL.test(String(value ?? '').trim())
}

export function ipv4ForSubmit(display: string): string {
  return formatIpv4Typing(display).trim()
}

export type Ipv4Validation =
  | { ok: true; value: string }
  | { ok: false; message: string }

export function validateIpv4ForSubmit(display: string): Ipv4Validation {
  const value = ipv4ForSubmit(display)
  if (!value) {
    return { ok: false, message: 'IP address is required.' }
  }
  if (!isValidIpv4(value)) {
    return {
      ok: false,
      message: 'Enter a complete IPv4 address (e.g. 192.168.1.10).',
    }
  }
  return { ok: true, value }
}
