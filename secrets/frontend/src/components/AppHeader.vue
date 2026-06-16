<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img v-if="!logoHidden" :src="logoSrc" alt="trinityX" class="tx-navbar-logo" @error="onLogoError" />
        </a>
      </li>
      <li class="tx-breadcrumb-item"><a :href="homeUrl" class="tx-breadcrumb-link">Home</a></li>
      <li class="tx-breadcrumb-item"><a href="#" class="tx-breadcrumb-link" @click.prevent>Secrets</a></li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { punAppAssetUrl } from '@/utils/publicAssets'
import { appUrlFromRuntime } from '@/utils/oodAppRoot'

const logoHidden = ref(false)

const homeUrl = computed(() => {
  const raw = appUrlFromRuntime()
  if (raw) {
    try {
      return `https://${new URL(raw).hostname}:8080`
    } catch {
      /* fall through */
    }
  }
  return `https://${window.location.hostname}:8080`
})

const logoSrc = computed(() => {
  if (logoHidden.value) return ''
  return punAppAssetUrl('static/img/logo.png')
})

function onLogoError() {
  logoHidden.value = true
}
</script>
