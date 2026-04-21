<template>
  <footer class="tx-footer">
    <div class="tx-footer-inner">
      <div class="tx-footer-left">
        &copy; 2023, made with &#10084;&#65039; by
        <a href="https://clustervision.com/" target="_blank" class="tx-footer-link">ClusterVision</a>
      </div>
      <div class="tx-footer-right">
        <a :href="licenseUrl" class="tx-footer-link" target="_blank">License</a>
        <a href="https://github.com/clustervision/trinityX" target="_blank" class="tx-footer-link">Documentation</a>
        <a href="https://support.clustervision.com/" target="_blank" class="tx-footer-link">Support</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const licenseUrl = computed(() => {
  const appUrl = window.APP_URL || ''
  return `${appUrl.replace(/\/$/, '')}/license`
})
</script>
