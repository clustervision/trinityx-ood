<script lang="ts" setup>
import { type PropType } from 'vue';
import EditConfig from '@/views/EditConfig.vue';
import RuleModals from '@/components/RuleModals.vue';
import { ref } from 'vue';
import { Modal } from 'bootstrap';

const props = defineProps({
  rulesFile: {
    type: String,
    required: true,
  },
  save_configuration: {
    type: Function,
    required: true,
  },
  Content: {
    type: String,
    required: true,
  },
  ContentType: {
    type: String as PropType<'JSON' | 'YAML'>,
    required: true,
  },

  update_configuration: {
    type: Function,
    required: true,
  },
  promQLurl: {
    type: String,
    required: true,
  },
  configuration: Object,
  updateClass: Function,
  ruleRow: Function,
  selectedClass: String,


});

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits(['toast']);

const new_config = props.configuration;

const uniqueModal = ref<Modal | null>(null);
const showModal = (id: number) => {
  const dymodal = document.getElementById(`rule_modal_${id}`);
  if (dymodal) {
    uniqueModal.value = new Modal(dymodal, {
      backdrop: true,
    });
    uniqueModal.value.show();
  } else {
    console.error(`Modal with ID rule_modal_${id} not found`);
  }
};


function deleteRule(count: number) {
  if (new_config?.groups?.[0]?.rules) {
    new_config.groups[0].rules.splice(count, 1);
    props.save_configuration(new_config, 'On Page')
  }
}

</script>

<template>

  <div class="container-xxl flex-grow-1 container-p-y" style="max-width: none">
    <span style="float: right;">
        <EditConfig
          :rulesFile = "rulesFile"
          :save_configuration = "save_configuration"
          :Content="Content"
          :ContentType="ContentType"
          @Toast="$emit('toast', $event)"
        />
      </span>
    <h4 class="fw-bold py-3 mb-4">
      <span class="text-muted fw-light"> Monitoring /</span> Alert Configurator
    </h4>

    <div class="card">
      <h5 class="card-header">Rules</h5>
      <div class="card-body">
        <div class="table-responsive text-nowrap">
          <RuleModals
            :promQLurl = "promQLurl"
            :configuration="configuration"
            :save_configuration = "save_configuration"
            :updateClass = "updateClass"
            :ruleRow = "ruleRow"
            :row = "{'alert': '', 'annotations': {'description': ''}, 'for': '', 'expr': '', 'labels': {'_trix_status': false, 'nhc': 'no', 'severity': 'info'}}"
            :index = 0
            :selectedClass="selectedClass"
            @Toast="$emit('toast', $event)"
          />
          <table id="alert-table" class="table table-bordered table-striped table-hover table-responsive">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Group</th>
                <th scope="col">Rule</th>
                <th scope="col">Enable</th>
                <th scope="col">NHC</th>
                <th scope="col">Priority</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody v-for="(groups, groupsIndex) in props.configuration?.groups" :key="groups.name">
              <tr v-for="(row, index) in groups.rules" :key="index">
                <th scope="row">{{ index + 1 }}</th>
                <td>{{ groups.name }}</td>
                <td>
                  <a href="#"  @click.prevent="showModal(index + 1)">{{ row.alert }}</a>
                  <input type="hidden" :id="`group_name_${groupsIndex + 1}`" :value="`${groups.name}`" />
                  <input type="hidden" :id="`rule_name_${index + 1}`" :value="`${row.alert}`" />
                  <input type="hidden" :id="`rule_description_${index + 1}`" :value="`${row.annotations.description}`" />
                  <input type="hidden" :id="`rule_for_${index + 1}`" :value="`${row.for}`" />
                  <input type="hidden" :id="`rule_editor_${index + 1}`" :value="`${row.expr}`" />
                </td>
                <td>
                  <div class="form-check form-switch mb-2">
                    <input class="form-check-input" type="checkbox" v-model="row.labels._trix_status" @click="props.update_configuration(index + 1);" :id="`rule_status_${index + 1}`" />
                    <label class="form-check-label" :for="`rule_status_${index + 1}`">{{ row.labels._trix_status ? 'ON' : 'OFF' }}</label>
                  </div>
                </td>
                <td>
                  <div class="form-check form-switch mb-2">
                    <input class="form-check-input" type="checkbox" v-model="row.labels.nhc" @click="props.update_configuration(index + 1);" :id="`rule_nhc_${index + 1}`" data-toggle="switch" :true-value="'yes'" false-value="no" />
                    <label class="form-check-label" :for="`rule_nhc_${index + 1}`">{{ row.labels.nhc === 'yes' ? 'ON' : 'OFF' }}</label>
                  </div>
                </td>
                <td>
                  <select :id="`severity_${index + 1}`" @change="props.update_configuration(index + 1);" v-model="row.labels.severity" :class="['form-select', 'form-select-sm', row.labels.severity === 'critical' ? 'btn-dark' : 'btn-' + row.labels.severity]">
                    <option class="btn-primary" value="">Set Priority</option>
                    <option class="btn-dark" value="critical" :selected="row.labels.severity === 'critical'">Critical</option>
                    <option class="btn-danger" value="danger" :selected="row.labels.severity === 'danger'">Danger</option>
                    <option class="btn-warning" value="warning" :selected="row.labels.severity === 'warning'">Warning</option>
                    <option class="btn-info" value="info" :selected="row.labels.severity === 'info'">Informational</option>
                  </select>
                </td>
                <td>
                  <div style="display: inline-block;" class="tooltip-wrapper" data-bs-toggle="tooltip" data-bs-html="true" data-bs-original-title="<i class='bx bxs-arrow-from-left bx-xs'></i> <span>Edit This Rule</span>">
                    <button class="tooltip-modal-link" id="actions" :data-bs-target="`#rule_modal_${index + 1}`" data-bs-toggle="modal">
                      <box-icon name='edit' color="#696cff" size="md"></box-icon>
                    </button>
                  </div>
                  <button style="display: inline-block;" class="tooltip-modal-link" @click.prevent="deleteRule(index);" id="actions" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class='bx bxs-arrow-from-left bx-xs'></i> <span>Delete This Rule</span>">
                    <box-icon name='trash' color="red" size="md" ></box-icon>
                  </button>
                  <RuleModals
                    :promQLurl = "promQLurl"
                    :configuration = "configuration"
                    :save_configuration = "save_configuration"
                    :updateClass = "updateClass"
                    :ruleRow = "ruleRow"
                    :row = "row"
                    :index = index+1
                    :selectedClass = "selectedClass"
                    @Toast = "$emit('toast', $event)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

</template>
