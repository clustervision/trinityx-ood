<template>
  <div>
    <!-- Modal -->
    <div class="modal fade" :id="props.modalId" tabindex="-1" aria-labelledby="modalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="modalLabel">Alerts Overview for <span style="color: blue;"><i>{{ props.hostname }}</i></span> [{{ props.ruleType }}]</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <table class="table table-striped table-bordered">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Rule</th>
                  <th>State</th>
                  <th>Severity</th>
                  <th>NHC</th>
                  <th>Exporter</th>
                  <th>Path</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(alert, index) in props.alerts" :key="alert.state">
                  <td>{{ index +1 }}</td>
                  <td>{{ alert.labels.alertname }}</td>
                  <td>{{ alert.state }}</td>
                  <td>{{ alert.labels.severity }}</td>
                  <td>{{ alert.labels.nhc }}</td>
                  <td>{{ alert.labels.exporter }}</td>
                  <td>{{ alert.labels.path }}</td>
                  <td>{{ alert.annotations.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

interface SpecificAlerts {
  activeAt: string;
  annotations: { description: string };
  labels: {
    alertname: string;
    category: string;
    class: string;
    description: string;
    disabled: boolean;
    exporter: string;
    hostname: string;
    instance: string;
    job: string;
    luna_group: string;
    nhc: boolean;
    severity: string;
    path: string;
    product: string;
    serial: string;
    vendor: string;
  };
  state: string;
  value: string;
}

const props = defineProps<{
  alerts: SpecificAlerts[];
  modalId: string;
  hostname: string;
  ruleType: string;
}>();

const emit = defineEmits(["modal-open", "modal-close"]);

onMounted(() => {
  const modalElement = document.getElementById(props.modalId);
  if (modalElement) {
    modalElement.addEventListener("shown.bs.modal", () => emit("modal-open"));
    modalElement.addEventListener("hidden.bs.modal", () => emit("modal-close"));
  }
});

onUnmounted(() => {
  const modalElement = document.getElementById(props.modalId);
  if (modalElement) {
    modalElement.removeEventListener("shown.bs.modal", () => emit("modal-open"));
    modalElement.removeEventListener("hidden.bs.modal", () => emit("modal-close"));
  }
});
</script>

<style scoped>
.modal-body {
  max-height: 400px;
  overflow-y: auto;
}
</style>
