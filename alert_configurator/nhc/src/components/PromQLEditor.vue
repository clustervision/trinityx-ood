<template>
   <div>
      <div class="promql"></div>
   </div>
 </template>
 
 <script lang="ts">
 import { ref, onMounted, watch } from 'vue';
 import {PromQLExtension} from '@prometheus-io/codemirror-promql';
 import {basicSetup} from 'codemirror';
 import {EditorState} from '@codemirror/state';
 import {EditorView} from '@codemirror/view';
 
 export default {
   name: "PromQLEditor",
 
   mounted() {
    
     try {
       const parentElement = document.querySelector('.promql');
       if (!parentElement) {
         console.error("Element with ID 'editor-container' not found.");
         return;
       }
 
       const promQL = new PromQLExtension();
       promQL.setComplete({ maxMetricsMetadata: 10000, remote: { httpErrorHandler: (error: string) => console.error(error), httpMethod: 'GET', url: "https://vmware-controller1.cluster:9090" } });
 
       new EditorView({
         state: EditorState.create({
           extensions: [basicSetup, promQL.asExtension()],
         }),
         parent: parentElement,
       });
 
       console.log("Editor initialized successfully.");
     } catch (error) {
       console.error("Error initializing the editor:", error);
     }
   },

 };
 
 </script>
 