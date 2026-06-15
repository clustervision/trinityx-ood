<script setup lang="ts">

defineProps({
  app_url: {
    type: String,
    required: true
  },
})
</script>

<template>
  <footer class="tx-footer">
    <div class="tx-footer-inner">
      <div class="tx-footer-left">
        &copy; 2026, Copyright ClusterVision Solutions
      </div>
      <div class="tx-footer-right">
        <a :href="`${$props.app_url}/api/v1/license`" class="tx-footer-link" target="_blank" rel="noopener noreferrer">License</a>
        <a href="https://docs.clustervision.com/" target="_blank" rel="noopener noreferrer" class="tx-footer-link">Docs</a>
        <a href="https://support.clustervision.com/" target="_blank" class="tx-footer-link">Support</a>
      </div>
    </div>
  </footer>
</template>
