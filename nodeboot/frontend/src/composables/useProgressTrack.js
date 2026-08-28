import { ref, onUnmounted, watch } from 'vue'

export function useProgressTrack(blockHeight, maxBlocks, minBlocks, blockWidth, gap) {
  const trackEl = ref(null)
  const blockCount = ref(maxBlocks)
  const trackHeight = ref(blockHeight * maxBlocks + (maxBlocks - 1) * gap)
  let observer = null

  function update() {
    const width = trackEl.value?.clientWidth
    if (!width) return
    const count = Math.max(minBlocks, Math.min(maxBlocks, Math.floor((width + gap) / (blockWidth + gap))))
    blockCount.value = count
    const blockSize = (width - (count - 1) * gap) / count
    trackHeight.value = blockSize * blockHeight + (blockHeight - 1) * gap
  }

  watch(trackEl, (el) => {
    observer?.disconnect()
    if (!el) return
    observer = new ResizeObserver(update)
    observer.observe(el)
    update()
  })

  onUnmounted(() => observer?.disconnect())

  return { trackEl, blockCount, trackHeight, update }
}
