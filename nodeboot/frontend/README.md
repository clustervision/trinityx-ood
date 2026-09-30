# TrinityX OOD Node Boot Frontend

Vue.js frontend for the TrinityX Open OnDemand Luna node boot dashboard.

This project provides the browser UI for watching nodes boot in real time. It works together with the nodeboot Flask backend in the `trinityx-ood` repository.

## Project structure

```text
.
├── index.html
├── package.json
├── vite.config.js
├── .env.production
├── .env.development.example
├── public/
│   ├── favicon.ico
│   ├── static/img/
│   └── vendor/
└── src/
    ├── main.js
    ├── App.vue
    ├── api.js
    ├── assets/styles.css
    ├── components/
    ├── composables/
    └── utils/
```

## Install

```bash
npm install
```

## Development

Copy `.env.development.example` to `.env.development` and set your OOD backend URL:

```env
VITE_NODEBOOT_BACKEND=https://your-ood-host/pun/sys/trinity_nodeboot
```

Then:

```bash
npm run dev
```

Vite proxies `/nodeboot-backend` to the Flask app.

## Build

```bash
npm run build
```

Output lands in:

```text
dist/
├── index.js
├── index.css
├── index.html
├── favicon.ico
├── static/
└── vendor/
```

## Deploy to trinityx-ood

Copy the contents of `dist/` into the Flask static directory:

```text
trinityx-ood/nodeboot/app/assets/
```

Ensure production `VITE_PUBLIC_BASE` matches how Flask serves assets (see `.env.production`).

## Technology stack

- Vue 3
- Vite 6
- Flask backend via `/api/status` and `/api/console/<node>`

## License

Part of the TrinityX software suite — GPL v3 or later.

