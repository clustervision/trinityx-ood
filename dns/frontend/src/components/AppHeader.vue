<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img :src="logoSrc" alt="Logo" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="homeUrl" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a href="#" class="tx-breadcrumb-link" @click.prevent>DNS Entries</a>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { appUrlFromRuntime, publicAssetUrl } from '@/utils'

const homeUrl = computed(() => {
  const raw = appUrlFromRuntime()
  if (raw) {
    try {
      return `https://${new URL(raw).hostname}:8080`
    } catch {
      /* fall through */
    }
  }
  return typeof window !== 'undefined' ? `https://${window.location.hostname}:8080` : '#'
})

const logoSrc = computed(() => publicAssetUrl('img/logo.png'))
</script>
