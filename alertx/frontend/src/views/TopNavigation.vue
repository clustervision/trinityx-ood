
<template>
  <nav class="navbar shadow-sm navbar-light">
    <ol class="breadcrumb bg-transparent d-flex align-items-center">
      <a href="/" aria-current="page" role="menuitem">
        <img :src="`${$props.url}/assets/logo.png`" class="img-logo" />
      </a>
      <li class="breadcrumb-item"><a class="align-middle" href="/">Home</a></li>
      <li class="breadcrumb-item"><a class="align-middle" :href="`${$props.url}`">AlertX</a></li>
    </ol>
  </nav>
</template>

<script lang="ts">

export default {
  name: "TopNavigation",
  props: {
    url: {
      type: String,
      required: true,
    },
  },
}

</script>
