// src/global.d.ts
export {};

declare global {
    interface Window {
        PROMQL_URL: string;
        APP_URL: string;
        statusAPI: string;
        TRIX_CONFIG: string;
    }
}

import jQuery from 'jquery';

declare global {
  interface Window {
    $: typeof jQuery;
    jQuery: typeof jQuery;
  }
}
