export function distributeBlocks(booted, booting, failed, total, blockCount) {
  const safeTotal = total || 1
  let bootedBlocks = Math.round((booted / safeTotal) * blockCount)
  let bootingBlocks = Math.round((booting / safeTotal) * blockCount)
  let failedBlocks = Math.round((failed / safeTotal) * blockCount)

  while (bootedBlocks + bootingBlocks + failedBlocks > blockCount) {
    if (failedBlocks > 0) failedBlocks--
    else if (bootingBlocks > 0) bootingBlocks--
    else bootedBlocks--
  }

  const blocks = []
  for (let i = 0; i < bootedBlocks; i++) blocks.push('b-booted')
  for (let i = 0; i < bootingBlocks; i++) blocks.push('b-booting')
  for (let i = 0; i < failedBlocks; i++) blocks.push('b-failed')
  while (blocks.length < blockCount) blocks.push('')
  return blocks
}

export function formatCount(value) {
  return value.toLocaleString()
}
