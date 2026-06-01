<script setup lang="ts">
defineProps<{ appUrl: string }>()
</script>

<template>
  <footer class="tx-footer">
    <div class="tx-footer-inner">
      <div class="tx-footer-left">
        &copy; 2026, made with &#10084;&#65039; by
        <a href="https://clustervision.com/" target="_blank" class="tx-footer-link">ClusterVision</a>
      </div>
      <div class="tx-footer-right">
        <a :href="`${appUrl}/api/v1/license`" class="tx-footer-link" target="_blank" rel="noopener">License</a>
        <a href="https://github.com/clustervision/trinityX" target="_blank" class="tx-footer-link" rel="noopener">Documentation</a>
        <a href="https://support.clustervision.com/" target="_blank" class="tx-footer-link" rel="noopener">Support</a>
      </div>
    </div>
  </footer>
</template>
