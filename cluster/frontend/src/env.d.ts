/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2026  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * @author      Yixin Zhang
 * @copyright   Copyright 2026, Luna2 Project[OOD]
 * @license     GPL
 * @version     2.0
 * @maintainer  Yixin Zhang
 * @email       yixin.zhang@clustervision.com
 * @status      Development
 */

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
