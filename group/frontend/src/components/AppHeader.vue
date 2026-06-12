<script setup lang="ts">
import { punAppAssetUrl } from '@/utils/publicAssets'

const logoUrl = punAppAssetUrl('static/img/logo.png')

defineProps({
  app_url: {
    type: String,
    required: true
  },
})
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
        <a :href="`${$props.app_url}`" class="tx-breadcrumb-link">Group</a>
      </li>
    </ol>
  </nav>
</template>


