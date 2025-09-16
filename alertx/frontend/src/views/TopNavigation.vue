
<script lang="ts" setup>
import Wizard from '@/components/Wizard.vue';

</script>
<script lang="ts">
export default {
  name: "TopNavigation",
  props: {
    url: {
      type: String,
      required: true,
    },

    promQLurl: {
      type: String,
      required: true,
    },
    configType: {
      type: String,
      required: true,
    },
    configuration: Object,
    save_configuration: {
      type: Function,
      required: true,
    },
  },
}

</script>
<template>
  <nav class="navbar shadow-sm navbar-light">
    <ol class="breadcrumb bg-transparent d-flex align-items-center">
      <a href="/" aria-current="page" role="menuitem">
        <img :src="`${$props.url}/assets/logo.png`" class="img-logo" />
      </a>
      <li class="breadcrumb-item"><a class="align-middle" href="/">Home</a></li>
      <li class="breadcrumb-item"><a class="align-middle" :href="`${$props.url}`">AlertX</a></li>
    </ol>
    <button type="button" class="btn btn-info" data-bs-toggle="modal" :data-bs-target="`#wizard_modal_${configType}`" data-bs-placement="top" title="Step-by-step guide to create an alert rule"><strong>Rule Wizard</strong></button>
    <Wizard :url="url" :PrometheusServer="promQLurl" configType="generic" :configuration="configuration" :save_configuration = "save_configuration" />
  </nav>
</template>


