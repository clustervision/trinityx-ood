<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

function parseTimestamp(timestampStr: string) {
  try {
    if (!timestampStr) return "";
    if (timestampStr.includes("Z00:00Z")){ timestampStr = timestampStr.replace("Z00:00Z", "Z"); }
    if (timestampStr.endsWith("Z")){ timestampStr = timestampStr.replace("Z", "+00:00"); }
    if (timestampStr.includes(".")){
      const datePart = timestampStr.split(".")[0];
      let fractionPart = timestampStr.split(".")[1];
      fractionPart = fractionPart.replace(/Z$/, ""); // Remove trailing Z if exists

      if (fractionPart.includes("+") || fractionPart.includes("-")){
        let fraction = fractionPart.split(/[+-]/)[0];
        const tz = fractionPart.split(/[+-]/)[1];
        fraction = fraction.substring(0, 6); // Trim to 6 digits
        timestampStr = `${datePart}.${fraction}+${tz}`;
      } else {
        timestampStr = `${datePart}.${fractionPart.substring(0, 6)}`;
      }
    }
    const dateObj = new Date(timestampStr);

    // For UTC TimeZone uncomment this block and comment out the Dynamic block
    // const offsetMinutes = dateObj.getTimezoneOffset();
    // const offsetHours = Math.abs(Math.floor(offsetMinutes / 60));
    // const offsetMins = Math.abs(offsetMinutes % 60);
    // const sign = offsetMinutes > 0 ? "-" : "+";
    // const utcOffset = `UTC${sign}${String(offsetHours).padStart(2, "0")}:${String(offsetMins).padStart(2, "0")}`;
    // const formattedDate = dateObj.toISOString().split("T")[0]; // "YYYY-MM-DD"
    // const formattedTime = dateObj.toTimeString().split(" ")[0]; // "HH:MM:SS"
    // return `${formattedDate} ${formattedTime} ${utcOffset}`;
    // For UTC TimeZone uncomment this block and comment out the Dynamic block

    // For Dynamic TimeZone
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const formattedDate = dateObj.toISOString().split("T")[0]; // "YYYY-MM-DD"
    const formattedTime = dateObj.toTimeString().split(" ")[0]; // "HH:MM:SS"
    return `${formattedDate} ${formattedTime} ${timeZone}`;
    // For Dynamic TimeZone

  } catch (error) {
    console.error("Invalid timestamp:", timestampStr, error);
    return "";
  }
}

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
      nhc: boolean,
      severity: string
  },
  lastEvaluation: string,
  name: string,
  query: string,
  state: string,
  type: string
}

const props = defineProps<{
  rule: Rule[];
  alerts: Alerts[];
  modalId: string;
  first_occurrence: string;
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
            <h5 class="modal-title" id="modalLabel">Alert Rule <span style="color: blue;"><i>{{ props.rule[0].name }}</i></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <table class="table table-striped table-bordered">
              <tbody>
                <tr>
                  <td><strong>Rule Name</strong></td>
                  <td>{{ props.rule[0].name }}</td>
                </tr>
                <tr>
                  <td><strong>Description</strong></td>
                  <td>{{ props.rule[0].annotations.description }}</td>
                </tr>
                <tr>
                  <td><strong>Query</strong></td>
                  <td>{{ props.rule[0].query }}</td>
                </tr>
                <tr>
                  <td><strong>State</strong></td>
                  <td>{{ props.rule[0].state }}</td>
                </tr>
                <tr>
                  <td><strong>Type</strong></td>
                  <td>{{ props.rule[0].type }}</td>
                </tr>
                <tr>
                  <td><strong>Health</strong></td>
                  <td>{{ props.rule[0].health }}</td>
                </tr>
                <tr>
                  <td><strong>Severity</strong></td>
                  <td>{{ props.rule[0].labels.severity }}</td>
                </tr>
                <tr>
                  <td><strong>Category</strong></td>
                  <td>{{ props.rule[0].labels.category }}</td>
                </tr>
                <tr>
                  <td><strong>Duration</strong></td>
                  <td>{{ props.rule[0].duration }}</td>
                </tr>
                <tr>
                  <td><strong>Evaluation Time</strong></td>
                  <td>{{ props.rule[0].evaluationTime }}</td>
                </tr>
                <tr>
                  <td><strong>Evaluation Duration</strong></td>
                  <td>{{ props.rule[0].duration }}</td>
                </tr>
                <tr>
                  <td><strong>First Occurrence</strong></td>
                  <td>{{ props.first_occurrence }}</td>
                </tr>
                <tr>
                  <td><strong>Last Evaluation</strong></td>
                  <td>{{ parseTimestamp(props.rule[0].lastEvaluation) }}</td>
                </tr>
                <tr>
                  <td><strong>Keep Firing For</strong></td>
                  <td>{{ props.rule[0].keepFiringFor }}</td>
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
                  <td>{{ alert.labels.hostname }}</td>
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

