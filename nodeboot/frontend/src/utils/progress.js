export function distributeBlocks(booted, booting, failed, unknown, total, blockCount) {
  const safeTotal = total || 1
  const counts = { 'b-booted': booted, 'b-booting': booting, 'b-unknown': unknown, 'b-failed': failed }
  const sized = Object.entries(counts).map(([cls, n]) => [cls, Math.round((n / safeTotal) * blockCount)])
  // rounding can overshoot by a block; trim from the end (failed first) until it fits
  let over = sized.reduce((sum, [, n]) => sum + n, 0) - blockCount
  for (let i = sized.length - 1; over > 0 && i >= 0; i--) {
    const take = Math.min(over, sized[i][1])
    sized[i][1] -= take
    over -= take
  }
  const blocks = sized.flatMap(([cls, n]) => Array(n).fill(cls))
  while (blocks.length < blockCount) blocks.push('')
  return blocks
}

export function formatCount(value) {
  return value.toLocaleString()
}
