<script setup>
import { computed } from 'vue'
import { punAppAssetUrl } from '../utils/publicAssets.js'

const homeUrl = computed(() => (typeof window === 'undefined' ? '#' : `${window.location.origin}/`))
const logoUrl = computed(() => punAppAssetUrl('static/img/logo.png'))
</script>

<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img :src="logoUrl" alt="Logo" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="homeUrl" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a href="#" class="tx-breadcrumb-link" @click.prevent>Node Boot Overview</a>
      </li>
    </ol>
  </nav>
</template>
