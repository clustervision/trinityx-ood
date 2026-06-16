<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  app_url: {
    type: String,
    required: true,
  },
})

const logoUrl = computed(() => `${props.app_url}/app/assets/static/img/logo.png`)
</script>

<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a href="/">
          <img :src="logoUrl" alt="Logo" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a href="/" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="`${$props.app_url}`" class="tx-breadcrumb-link">Switch</a>
      </li>
    </ol>
  </nav>
</template>
