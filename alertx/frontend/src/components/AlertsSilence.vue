<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";

const startAt = ref('');
const endAt = ref('');

function applySilence() {
  // Use `startAt.value` and `endAt.value` as ISO strings for the POST body
  console.log(props.alerts);
  console.log("Start:", startAt.value);
  console.log("End:", endAt.value);
  // convert to UTC ISO format if needed
}
// methods: {
//   open() {
//     const modal = new bootstrap.Modal(document.getElementById(this.modalId));
//     modal.show();
//     this.$emit("modal-open");
//   },
//   close() {
//     const modal = bootstrap.Modal.getInstance(document.getElementById(this.modalId));
//     modal.hide();
//     this.$emit("modal-close");
//   }
// }

const props = defineProps<{
  // rule: Rule;
  alerts: [];
  // alerts: Alerts[];
  modalId: string;
  // first_occurrence: string;
  // ruleName: string;
}>();

// const emit = defineEmits(["html", "modal-open", "modal-close"]);

// const hostList = ref<string[]>([]);

// watch(
//   () => props.alerts,
//   async (alerts) => {
//     try {
//       hostList.value = [];
//       for (const alert of alerts) {
//         if (!alert?.labels?.hostname) {
//           // console.warn("Missing hostname in alert:", alert);
//           hostList.value.push(""); // Push an empty string for missing hostnames
//           continue;
//         }
//         const parsedHostname = await new Promise<string>((resolve) => {
//           emit("html", alert.labels.hostname, resolve);
//         });
//         hostList.value.push(parsedHostname);
//       }
//     } catch (error) {
//       console.error("Error parsing hostnames:", error);
//       hostList.value = []; // Fallback to an empty array
//     }
//   },
//   { immediate: true }
// );

// onMounted(() => {
//   const modalElement = document.getElementById(props.modalId);
//   if (modalElement) {
//     modalElement.addEventListener("shown.bs.modal", () => emit("modal-open"));
//     modalElement.addEventListener("hidden.bs.modal", () => emit("modal-close"));
//   }
// });

// onUnmounted(() => {
//   const modalElement = document.getElementById(props.modalId);
//   if (modalElement) {
//     modalElement.removeEventListener("shown.bs.modal", () => emit("modal-open"));
//     modalElement.removeEventListener("hidden.bs.modal", () => emit("modal-close"));
//   }
// });
</script>

<style scoped>
.modal-body {
  max-height: 650px;
  overflow-y: auto;
}
</style>



<template>
  <div>
    <!-- Modal -->
    <div class="modal fade" :id="props.modalId" tabindex="-1" aria-labelledby="modalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="modalLabel">Silent Alert(s)</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">

            <form class="row g-3 mb-4">
              <div class="col-md-5">
                <label for="startAt" class="form-label">Start Time</label>
                <input type="datetime-local" class="form-control" id="startAt" v-model="startAt">
              </div>
              <div class="col-md-5">
                <label for="endAt" class="form-label">End Time</label>
                <input type="datetime-local" class="form-control" id="endAt" v-model="endAt">
              </div>
              <div class="col-md-2 d-flex align-items-end">
                <button type="button" class="btn btn-primary w-100" @click="applySilence">
                  Apply Silence
                </button>
              </div>
            </form>


            <table class="table table-striped table-bordered">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Alert</th>
                  <th>Hostname</th>
                </tr>
              </thead>
              <tbody>

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
<!-- POST https://<alertmanager-host>:9093/api/v2/silences
{
  "matchers": [
    {
      "name": "alertname",
      "value": "ServerDown",
      "isRegex": false
    },
    {
      "name": "hostname",
      "value": "node002.cluster",
      "isRegex": false
    }
  ],
  "startsAt": "2025-05-13T08:00:00Z",
  "endsAt": "2025-05-14T08:00:00Z",
  "createdBy": "admin",
  "comment": "Silence for maintenance"
} -->


<!--

curl -X POST https://vmware-controller1.cluster:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -u "admin:z80ea5dbbce33DZ2z420" \
  -d '{
    "matchers": [
      {
        "name": "alertname",
        "value": "ServerDown",
        "isRegex": false
      },
      {
        "name": "hostname",
        "value": "node002.cluster",
        "isRegex": false
      }
    ],
    "startsAt": "2025-05-13T08:00:00Z",
    "endsAt": "2025-05-14T08:00:00Z",
    "createdBy": "admin",
    "comment": "Silence for maintenance"
  }'

  -->

  <!--

  curl -s -u admin:your_password https://vmware-controller1.cluster:9093/api/v2/silences

[
  {
    "id": "f7c4539b-3381-49d4-9bc1-123456789abc",
    "status": {
      "state": "active"
    },
    "matchers": [...],
    "startsAt": "...",
    "endsAt": "...",
    ...
  }
]


  -->
