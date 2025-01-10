// src/global.d.ts
export {};

declare global {
    interface Window {
        PROMQL_URL: string;
        APP_URL: string;
        statusAPI: string;
        ResetNode: string;
    }
}
