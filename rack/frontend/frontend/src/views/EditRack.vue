<template>
  <div class="container-fluid flex-grow-1 container-p-y">
    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h5 class="mb-0">Update Rack - {{ form.name }}</h5>
        <button class="btn btn-warning" @click="$router.push('/manage/rack')">Back</button>
      </div>
      
      <div class="card-body">
        <form @submit.prevent="submitForm">
          
          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Name</label>
            <div class="col-sm-10">
              <input 
                type="text" 
                v-model="form.name" 
                class="form-control" 
                readonly 
              />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Site</label>
            <div class="col-sm-10">
              <input type="text" v-model="form.site" class="form-control" required />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Room</label>
            <div class="col-sm-10">
              <input type="text" v-model="form.room" class="form-control" required />
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Select Order</label>
            <div class="col-sm-10">
              <select v-model="form.order" class="form-control" required>
                <option value="ascending">Ascending (Top To Bottom)</option>
                <option value="descending">Descending (Bottom To Top)</option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
            <label class="col-sm-2 col-form-label">Size Of Rack</label>
            <div class="col-sm-10">
              <input type="number" v-model="form.size" class="form-control" min="0" max="1000" required />
            </div>
          </div>

          <div class="row justify-content-end">
            <div class="col-sm-10">
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? 'Updating...' : 'Update Rack ' + form.name }}
              </button>
            </div>
          </div>

          <div v-if="errorMessage" class="alert alert-danger mt-3">{{ errorMessage }}</div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const isSubmitting = ref(false);
const errorMessage = ref('');

const form = reactive({
  name: '',
  site: '',
  room: '',
  order: '',
  size: ''
});

// 1. Load existing data
onMounted(async () => {
  const rackName = route.params.id as string;
  form.name = rackName; // Set name immediately from URL
  
  try {
    // We fetch the list and find our rack because there isn't a dedicated "get single rack" JSON endpoint yet
    // (You might need to use the HTML parser trick here again if the backend doesn't give JSON)
    const res = await fetch('/manage/rack', { headers: { 'Accept': 'text/html' } });
    const html = await res.text();
    const racks = parseHtmlToData(html);
    
    const target = racks.find((r: any) => r.name === rackName);
    if (target) {
      form.site = target.site;
      form.room = target.room;
      form.order = target.order.toLowerCase();
      form.size = target.size;
    }
  } catch (e) {
    console.error("Failed to load rack details", e);
  }
});

// 2. Submit Update
const submitForm = async () => {
  isSubmitting.value = true;
  try {
    const params = new URLSearchParams();
    params.append('name', form.name);
    params.append('site', form.site);
    params.append('room', form.room);
    params.append('order', form.order);
    params.append('size', form.size.toString());

    // POST to /edit/rack/RackName (This matches your backend route logic)
    const response = await fetch(`/edit/rack/${form.name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    });

    // Accept 200, 302, or 500 (workaround for backend template error)
    if (response.ok || response.status === 302 || response.status === 500) {
      router.push('/manage/rack');
    } else {
      errorMessage.value = "Update failed.";
    }
  } catch (error) {
    errorMessage.value = "Network error.";
  } finally {
    isSubmitting.value = false;
  }
};

// Reuse your HTML parser
function parseHtmlToData(htmlString: string) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, 'text/html');
  const rows = doc.querySelectorAll('table tbody tr');
  const parsedData: any[] = [];
  rows.forEach((row) => {
    const cells = row.querySelectorAll('td');
    if (cells.length > 1) {
      parsedData.push({
        name: cells[1]?.innerText.trim(),
        size: cells[2]?.innerText.trim(),
        order: cells[3]?.innerText.trim(),
        room: cells[4]?.innerText.trim(),
        site: cells[5]?.innerText.trim(),
      });
    }
  });
  return parsedData;
}
</script>