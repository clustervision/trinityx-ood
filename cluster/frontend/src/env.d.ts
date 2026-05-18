// // src/global.d.ts
// export {};

// declare global {
//     interface Window {
//         APP_URL: string;
//     }
// }

// import jQuery from 'jquery';

// declare global {
//   interface Window {
//     $: typeof jQuery;
//     jQuery: typeof jQuery;
//   }
// }

// declare module '*.vue' {
//   import type { DefineComponent } from 'vue'

//   const component: DefineComponent<
//     Record<string, unknown>,
//     Record<string, unknown>,
//     unknown
//   >

//   export default component
// }

/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<
    Record<string, unknown>,
    Record<string, unknown>,
    unknown
  >

  export default component
}

interface Window {
  APP_URL: string
  $: typeof import('jquery')
  jQuery: typeof import('jquery')
}
