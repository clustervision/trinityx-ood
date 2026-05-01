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
        <a href="#" class="tx-breadcrumb-link" @click.prevent>Nodes</a>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { publicAssetUrl } from '../utils/publicAssets.js'

/** Same scheme as the page (HTTPS in deploy) — avoids hard-coded http from VITE_NODE_BACKEND. */
const homeUrl = computed(() => {
  if (typeof window === 'undefined') return '#'
  return `${location.protocol}//${location.hostname}:8080`
})

/** `public/img/logo.png`, prefixed with Vite `base` in production. */
const logoSrc = computed(() => publicAssetUrl('img/logo.png'))
</script>
