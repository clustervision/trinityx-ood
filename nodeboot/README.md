# Node Boot

Live boot and provisioning dashboard for TrinityX compute nodes, served
through Open OnDemand.

Node Boot shows, per OS image and per Luna group, how far every node has come
through its provisioning run: discovered → downloaded → unpacking → booted.
Each group renders as an animated phase chart with per-phase percentages;
failed nodes are listed with the reason, and clicking a node opens its recent
console output so the failure can be read without leaving the browser.

## How it works

- **Backend** (`app.py`): a Flask application that polls the Luna daemon
  (`/config/node`, `/monitor/status`, `/config/osimage`) and reduces the raw
  installer states into three visible phases plus booted/failed per
  (osimage, group) pair. Only an explicit `install.error` counts as failed;
  a node with no monitor entry at all is reported as "not started".
- **Console panel** (`/api/console/<node>`): captures the node's console
  live over Serial-over-LAN via the `sol-grab` service on the provisioning
  controller — an on-demand, bounded grab (capped worker pool, short
  capture window), so large clusters cannot pile up BMC sessions. The
  service unit is installed by the `trinity/node-console` ansible role.
- **Frontend** (`app/`): a Vue 3 single-page application (TypeScript, built
  with Vite). The built bundle is committed under `app/assets/` together with
  the vendored Geist fonts, so the app serves fully offline — no CDN access
  is needed on an air-gapped cluster. The page polls the backend every two
  seconds; polling pauses while a modal is open.

## Installation

This package requires `python3` and the modules listed in `requirements.txt`:

```
pip install -r requirements.txt
```

## Integration

To integrate this app inside Open OnDemand:

- Install `python3` and `python3-pip`
- Clone the repository to `/var/www/ood/apps/sys/`
- Install the python modules from `requirements.txt`

## Verifying the backend logic

`app.py` carries a self-check that pins the state mapping and grouping
behaviour:

```
python3 -c "from app import demo; demo()"
```
