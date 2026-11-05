<script lang="ts" setup>
import { computed } from 'vue'
import Wizard from '@/components/Wizard.vue'
import { appUrlFromRuntime, punAppAssetUrl } from '@/utils/publicAssets'

const props = defineProps<{
  url: string
  promQLurl: string
  configType: string
  configuration?: object
  save_configuration: (config: object) => void
}>()

const homeUrl = computed(() => {
  const raw = appUrlFromRuntime() || props.url || ''
  if (raw) {
    try {
      return `https://${new URL(raw).hostname}:8080`
    } catch {
      /* fall through */
    }
  }
  return typeof window !== 'undefined' ? `https://${window.location.hostname}:8080` : '#'
})

const logoSrc = computed(() => punAppAssetUrl('static/img/logo.png'))
</script>

<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img :src="logoSrc" alt="trinityX" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="homeUrl" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="url" class="tx-breadcrumb-link">AlertX</a>
      </li>
    </ol>
    <button
      type="button"
      class="btn btn-info tx-navbar-action"
      data-bs-toggle="modal"
      :data-bs-target="`#wizard_modal_${configType}`"
      data-bs-placement="top"
      title="Step-by-step guide to create an alert rule"
    >
      <strong>Rule Wizard</strong>
    </button>
    <Wizard
      :url="url"
      :PrometheusServer="promQLurl"
      configType="generic"
      :configuration="configuration"
      :save_configuration="save_configuration"
    />
  </nav>
</template>
