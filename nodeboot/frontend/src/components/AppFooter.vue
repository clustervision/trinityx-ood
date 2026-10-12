<script setup>
import { getAppUrl } from '../api.js'

const licenseUrl = `${getAppUrl()}/license`
</script>

<template>
  <footer class="tx-footer">
    <div class="tx-footer-inner">
      <div class="tx-footer-left">
        © 2023, made with ❤️ by
        <a href="https://clustervision.com/" target="_blank" rel="noopener noreferrer" class="tx-footer-link">ClusterVision</a>
      </div>
      <div class="tx-footer-right">
        <a :href="licenseUrl" class="tx-footer-link" target="_blank" rel="noopener noreferrer">License</a>
        <a href="https://docs.clustervision.com/" target="_blank" rel="noopener noreferrer" class="tx-footer-link">Docs</a>
        <a href="https://support.clustervision.com/" target="_blank" rel="noopener noreferrer" class="tx-footer-link">Support</a>
      </div>
    </div>
  </footer>
</template>
