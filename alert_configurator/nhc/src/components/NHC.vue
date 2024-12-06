<script setup lang="ts">
defineProps<{
  //trix_config: string
  show: boolean
  updateShow:string
  metrics: undefined
  insertAtCursor: void
}>()
</script>

<template>
  <b-modal
    :visible="localShow"
    @hide="toggle(false)"
    title="Metrics Explorer"
    size="lg"
    centered
    class="metrics-explorer"
  >
    <b-modal-header close-button>
      <template #default>Metrics Explorer</template>
    </b-modal-header>
    <b-modal-body>
      <p v-for="metric in metrics" :key="metric" class="metric" @click="handleMetricClick(metric)">
        {{ metric }}
      </p>
    </b-modal-body>
  </b-modal>


</template>


<script lang="ts">
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

export default {
  name: 'NHC',
  props: {
    show: {
      type: Boolean,
      required: true,
    },
    metrics: {
      type: Array,
      required: true,
    },
  },
  emits: ['update:show', 'insert-at-cursor'],
  computed: {
    localShow: {
      get() {
        return this.show
      },
      set(value) {
        this.$emit('update:show', value)
      },
    },
  },
  methods: {
    handleMetricClick(metric) {
      this.$emit('insert-at-cursor', metric)
      this.localShow = false
    },
    toggle(value) {
      this.localShow = value
    },
  },
}
</script>

<style scoped>
.metrics-explorer .metric {
  cursor: pointer;
  color: #007bff;
  margin-bottom: 0.5rem;
}
.metrics-explorer .metric:hover {
  text-decoration: underline;
}
.metrics-explorer.modal-dialog {
  max-width: 750px;
  overflow-wrap: break-word;
}

.metrics-explorer .metric {
  cursor: pointer;
  margin: 0;
  padding: 5px;
}

.metrics-explorer .metric:hover {
  background: #efefef;
}

</style>
