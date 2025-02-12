<template>
    <div v-if="visible" class="popup-overlay">
      <div class="popup-content">
        <h3>Security Warning</h3>
        <p>The server you are trying to connect to uses a self-signed certificate. This may pose a security risk. Do you want to proceed?</p>
        <button @click="onConfirm">Proceed</button>
        <button @click="onCancel">Cancel</button>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'SecurityWarningPopup',
    props: {
      visible: {
        type: Boolean,
        required: true,
      },
    },
    emits: ['confirm', 'cancel'],
    methods: {
      onConfirm() {
        this.$emit('confirm');
      },
      onCancel() {
        this.$emit('cancel');
      },
    },
  });
  </script>
  
  <style scoped>
  .popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .popup-content {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
  }
  </style>