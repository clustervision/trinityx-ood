<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import axios from 'axios';
import { Modal } from 'bootstrap';

const startAt = ref('');
const endAt = ref('');
const comment = ref('');
const errorMessage = ref<string[]>([]);

const useDateTime = ref("false")  // toggle

const days = ref(0)
const hours = ref(0)
const minutes = ref(0)

function blockInvalidKeys(event: Event) {
  const invalidKeys = ['-', '+', 'e', '.', 'E']
  const key = (event as KeyboardEvent).key;
  if (invalidKeys.includes(key)) {
    event.preventDefault()
  }
}

function validateDays(event: Event) {
  const target = event.target as HTMLInputElement | null;
  if (!target) {
    days.value = 0;
    return;
  }
  const value = parseInt(target.value);
  if (isNaN(value)) {
    days.value = 0
  } else if (value > 30) {
    days.value = 30
  } else if (value < 0) {
    days.value = 0
  } else {
    days.value = value
  }
}

async function applySilence() {
  const payloads: {
    matchers: { name: string; value: string; isRegex: boolean }[];
    startsAt: string;
    endsAt: string;
    createdBy: string;
    comment: string;
  }[] = [];

  const uniqueAlerts = props.alerts.map(alert => ({
    alertname: alert.alert,
    hostname: alert.hostname || null
  }));

  for (const alert of uniqueAlerts) {
    const matchers = [
      {
        name: "alertname",
        value: alert.alertname,
        isRegex: false
      }
    ];

    if (alert.hostname) {
      matchers.push({
        name: "hostname",
        value: alert.hostname,
        isRegex: false
      });
    }

    if (useDateTime.value === 'false') {
      if (!days.value && !hours.value && !minutes.value) {
        errorMessage.value.push(`Please Provide either day or hours or minutes or combinations of them.`);
        return;
      }
      const now = new Date();
      const endTime = new Date(now.getTime() + (days.value * 24 * 60 * 60 * 1000) + (hours.value * 60 * 60 * 1000) + (minutes.value * 60 * 1000));
      startAt.value = now.toISOString();
      endAt.value = endTime.toISOString();
    } else {
      if (startAt.value === '') {
        errorMessage.value.push(`Start time is required.`);
      }
      if (endAt.value === '') {
        errorMessage.value.push(`End time is required.`);
      }
      if (errorMessage.value.length > 0) {
        return;
      }
      const startDate = new Date(startAt.value);
      const endDate = new Date(endAt.value);
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        errorMessage.value.push(`Invalid date format for Start or End time.`);
        continue;
      }
      if (startDate >= endDate) {
        errorMessage.value.push(`Start time must be before End time.`);
        continue;
      }
    }
    

    const payload = {
      matchers,
      startsAt: new Date(startAt.value).toISOString(),
      endsAt: new Date(endAt.value).toISOString(),
      createdBy: "admin",
      comment: comment.value || "Silence for maintenance"
    };

    payloads.push(payload);
  }
  for (const payload of payloads) {
    try {
      const response = await axios.post(props.silenceAPI, payload);
      const message = `Alert ${payload.matchers[0].value} silenced successfully. Silence ID: <strong>${response.data.silenceID}</strong>`;
      emit('silence-message', message);
      const modalEl = document.getElementById("silenceAlerts");
      if (modalEl) {
        const bootstrapModal = Modal.getInstance(modalEl) || new Modal(modalEl);
        bootstrapModal.hide();
      }
    } catch (error) {
      console.error("Error creating silence:", error);
    }
  }
}

const props = defineProps<{
  alerts: { alert: string; hostname: string }[];
  modalId: string;
  silenceAPI: string;
}>();

const emit = defineEmits(["silence-message", "modal-open", "modal-close"]);

onMounted(() => {
  const modalElement = document.getElementById(props.modalId);
  if (modalElement) {
    modalElement.addEventListener("shown.bs.modal", () => emit("modal-open"));
    modalElement.addEventListener("hidden.bs.modal", () => {
      emit("modal-close");
      startAt.value = '';
      endAt.value = '';
      comment.value = '';
      errorMessage.value = [];
    });
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
.silent-choose {
  background-color: #cbdef0; /* light blue */
}
</style>

<template>
  <div>
    <!-- Modal -->
    <div class="modal fade" :id="props.modalId" tabindex="-1" aria-labelledby="modalLabel">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="modalLabel">Silent Alert(s)</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">

            <div v-for="(msg, index) in errorMessage" :key="index" class="alert alert-danger" role="alert" v-html="msg"></div>
            <form>
              <div class="row g-3 mb-4">

                <div class="col-12 p-3 rounded border silent-choose">
                  <label class="form-label d-block">Silent Mode Start</label>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="fromNow" value="false" v-model="useDateTime">
                    <label class="form-check-label" for="fromNow">Silent from Now</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="fromTime" value="true" v-model="useDateTime">
                    <label class="form-check-label" for="fromTime">Silent from a Specific Time</label>
                  </div>
                </div>
                
                <!-- Option 1: Datetime-local inputs -->
                <template v-if="useDateTime === 'true'">
                  <div class="col-md-6">
                    <label for="startAt" class="form-label">Start Time</label>
                    <input type="datetime-local" class="form-control" id="startAt" v-model="startAt">
                  </div>
                  <div class="col-md-6">
                    <label for="endAt" class="form-label">End Time</label>
                    <input type="datetime-local" class="form-control" id="endAt" v-model="endAt">
                  </div>
                </template>

                <!-- Option 2: Day / Hour / Minute -->
                <template v-else>
                  <div class="col-md-4">
                    <label for="days" class="form-label">Days</label>
                    <input type="number" class="form-control" id="days" v-model.number="days" min="0" max="30" @keydown="blockInvalidKeys" @input="validateDays" @paste.prevent >
                  </div>
                  <div class="col-md-4">
                    <label for="hours" class="form-label">Hours</label>
                    <input type="number" class="form-control" id="hours" v-model.number="hours" min="0" max="23" @keydown="blockInvalidKeys">
                  </div>
                  <div class="col-md-4">
                    <label for="minutes" class="form-label">Minutes</label>
                    <input type="number" class="form-control" id="minutes" v-model.number="minutes" min="0" max="59" @keydown="blockInvalidKeys">
                  </div>
                </template>
              </div>
              <div class="row g-3 mb-4">
                <div class="col-md-10">
                  <label for="comment" class="form-label">Comment</label>
                  <textarea type="text" class="form-control" id="comment" placeholder="Comment"></textarea>
                </div>
                <div class="col-md-2 d-flex align-items-end">
                  <button type="button" class="btn btn-primary w-100" @click="applySilence">Apply Silence</button>
                </div>
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
                <tr v-for="(alert, index) in props.alerts" :key="index">
                  <td>{{ index + 1 }}</td>
                  <td>{{ alert.alert }}</td>
                  <td>{{ alert.hostname }}</td>
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
