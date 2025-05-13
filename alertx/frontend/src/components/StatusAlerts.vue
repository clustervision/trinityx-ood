<template>
  <div>
    <!-- Modal -->
    <div class="modal fade" :id="props.modalId" tabindex="-1" aria-labelledby="modalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="modalLabel">Alert Rule <span style="color: blue;"><i>{{ props.rule.name }}</i></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <table class="table table-striped table-bordered">
              <tbody>
                <tr>
                  <td><strong>Rule Name</strong></td>
                  <td>{{ props.rule.name }}</td>
                </tr>
                <tr>
                  <td><strong>Description</strong></td>
                  <td>{{ props.rule.annotations.description }}</td>
                </tr>
                <tr>
                  <td><strong>Query</strong></td>
                  <td>{{ props.rule.query }}</td>
                </tr>
                <tr>
                  <td><strong>State</strong></td>
                  <td>{{ props.rule.state }}</td>
                </tr>
                <tr>
                  <td><strong>Type</strong></td>
                  <td>{{ props.rule.type }}</td>
                </tr>
                <tr>
                  <td><strong>Health</strong></td>
                  <td>{{ props.rule.health }}</td>
                </tr>
                <tr>
                  <td><strong>Severity</strong></td>
                  <td>{{ props.rule.labels.severity }}</td>
                </tr>
                <tr>
                  <td><strong>Category</strong></td>
                  <td>{{ props.rule.labels.category }}</td>
                </tr>
                <tr>
                  <td><strong>Duration</strong></td>
                  <td>{{ props.rule.duration }}</td>
                </tr>
                <tr>
                  <td><strong>Evaluation Time</strong></td>
                  <td>{{ props.rule.evaluationTime }}</td>
                </tr>
                <tr>
                  <td><strong>Evaluation Duration</strong></td>
                  <td>{{ props.rule.duration }}</td>
                </tr>
                <tr>
                  <td><strong>Last Evaluation</strong></td>
                  <td>{{ props.rule.lastEvaluation }}</td>
                </tr>
                <tr>
                  <td><strong>Keep Firing For</strong></td>
                  <td>{{ props.rule.keepFiringFor }}</td>
                </tr>

              </tbody>
            </table>
              <table class="table table-striped table-bordered">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Category</th>
                  <th>Class</th>
                  <th>Exporter</th>
                  <th>Hostname</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(alert, index) in props.alerts" :key="alert.state">
                  <td>{{ index +1 }}</td>
                  <td>{{ alert.labels.category }}</td>
                  <td>{{ alert.labels.class }}</td>
                  <td>{{ alert.labels.exporter }}</td>
                  <td v-html="hostList[index]"></td>
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
import { onMounted, onUnmounted, ref, watch } from "vue";

interface Alerts {
  activeAt: string;
  annotations: { description: string };
  labels: {
    alertname: string;
    exporter: string;
    hostname: string;
    category: string;
    class: string;
    instance: string;
    job: string;
    luna_group: string;
    disabled: boolean | null;
    nhc: boolean | null;
    severity: string;
  };
  state: string;
  value: string;
}


interface Rule {
  annotations: { description: string },
  duration: number,
  evaluationTime: number,
  health: string,
  keepFiringFor: number,
  labels: {
      category: string,
      severity: string
  },
  lastEvaluation: string,
  name: string,
  query: string,
  state: string,
  type: string
}

const props = defineProps<{
  rule: Rule;
  alerts: Alerts[];
  modalId: string;
  // ruleName: string;
}>();

const emit = defineEmits(["html", "modal-open", "modal-close"]);

const hostList = ref<string[]>([]);

watch(
  () => props.alerts,
  async (alerts) => {
    try {
      hostList.value = [];
      for (const alert of alerts) {
        if (!alert?.labels?.hostname) {
          // console.warn("Missing hostname in alert:", alert);
          hostList.value.push(""); // Push an empty string for missing hostnames
          continue;
        }
        const parsedHostname = await new Promise<string>((resolve) => {
          emit("html", alert.labels.hostname, resolve);
        });
        hostList.value.push(parsedHostname);
      }
    } catch (error) {
      console.error("Error parsing hostnames:", error);
      hostList.value = []; // Fallback to an empty array
    }
  },
  { immediate: true }
);

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
  max-height: 650px;
  overflow-y: auto;
}
</style>
