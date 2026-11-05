// // src/global.d.ts


declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<
    Record<string, unknown>,
    Record<string, unknown>,
    unknown
  >

  export default component
}

declare module '*.png' {
  const src: string
  export default src
}

interface Window {
  APP_URL: string
  $: typeof import('jquery')
  jQuery: typeof import('jquery')
}
