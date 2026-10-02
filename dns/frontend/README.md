# TrinityX DNS (Vue 3 + TypeScript)

Frontend for Luna2 DNS management. Backend: `../trinityx-ood/dns`.

## Development

```bash
cp .env.development.example .env.development
# Set VITE_APP_URL to your Flask app (e.g. http://controller:7755 or OOD pun URL)

npm install
npm run dev
```

Open http://localhost:5174 — API is proxied via `/dns-backend`.

## Production build

```bash
npm run build
```

Copy `dist/index.js`, `dist/index.css`, fonts, and `public/icons` into:

`/trinity/local/ondemand/3.0/dns/app/assets/`

Then `touch /trinity/local/ondemand/3.0/dns/tmp/restart.txt` on the controller.

## UI

- Inventory: Network, Host, IP Address, Actions (edit / delete icons)
- Add / Edit modal: three fields in one row (per design)
- Host/network: max 200 chars, table shows 25 + `...`
- IP field keeps `.` separators while typing
