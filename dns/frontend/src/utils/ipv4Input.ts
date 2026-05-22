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

export function ipv4ForSubmit(display: string): string {
  return formatIpv4Typing(display).trim()
}
