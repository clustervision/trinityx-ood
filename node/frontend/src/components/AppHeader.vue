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

<script setup lang="ts">
import { computed } from 'vue'
import { punAppAssetUrl } from '../utils/publicAssets'

const homeUrl = computed((): string => {
  if (typeof window === 'undefined') return '#'
  const appUrl = String(
    (window as Window & { APP_URL?: string }).APP_URL || ''
  ).trim()
  if (appUrl) return appUrl.replace(/\/+$/, '') + '/'
  return `${location.protocol}//${location.host}/`
})

const logoSrc = computed((): string => punAppAssetUrl('img/logo.png'))
</script>
