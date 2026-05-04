// src/global.d.ts
export {};

declare global {
    interface Window {
        APP_URL: string;
    }
}

import jQuery from 'jquery';

declare global {
  interface Window {
    $: typeof jQuery;
    jQuery: typeof jQuery;
  }
}
