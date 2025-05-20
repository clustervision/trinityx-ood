<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import axios from 'axios';
import { Modal } from 'bootstrap';

const startAt = ref('');
const endAt = ref('');
const comment = ref('');
const errorMessage = ref<string[]>([]);

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

    if (startAt.value === '') {
      errorMessage.value.push(`Start time is required.`);
    }
    if (endAt.value === '') {
      errorMessage.value.push(`End time is required.`);
    }
    if (errorMessage.value.length > 0) {
      return;
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
                <div class="col-md-6">
                  <label for="startAt" class="form-label">Start Time</label>
                  <input type="datetime-local" class="form-control" id="startAt" v-model="startAt">
                </div>
                <div class="col-md-6">
                  <label for="endAt" class="form-label">End Time</label>
                  <input type="datetime-local" class="form-control" id="endAt" v-model="endAt">
                </div>
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
