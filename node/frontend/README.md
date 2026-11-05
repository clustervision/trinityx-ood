# TrinityX OOD Node Frontend

Vue.js frontend for the TrinityX Open OnDemand Luna node management application.

This project provides the browser UI for managing Luna nodes from Open OnDemand. It is designed to work together with the node Flask backend application in the `trinityx-ood` repository. The Flask backend runs inside Open OnDemand through Passenger, exposes the `/api/v1` routes, talks to Luna, and serves the built frontend assets.

## Overview

The frontend is a Vite, Vue 3, and TypeScript application. It does not talk to Luna directly. All Luna operations go through the Flask backend.

The application currently supports:

- listing Luna nodes
- searching and sorting the node table
- adding a node
- editing a node
- renaming a node
- cloning a node
- deleting a node
- managing node interfaces
- suggesting the next free IPv4 address
- running OS Grab
- running OS Push
- showing inherited source labels such as `NODE`, `GROUP`, `OS IMAGE`, and `DEFAULT`
- editing long text fields through an expanded editor
- base64 handling for script and editor-style fields before sending data to the backend

## Runtime architecture

```text
Browser
  |
  | Vue frontend
  |
Open OnDemand Passenger app
  |
  | Flask backend from trinityx-ood
  |
Luna API / Luna CLI / Luna daemon
```

In development, Vite serves the frontend and can proxy API calls to the Flask backend.

In production, the frontend is built with `npm run build`. The generated static assets are copied into the Flask Open OnDemand app, where they are served by the Passenger-running backend.

## Repository role

This repository contains only the frontend code.

The backend is maintained separately in the `trinityx-ood` repository. That backend is responsible for:

- running under Open OnDemand Passenger
- serving the Vue build output
- exposing the node API endpoints under `/api/v1`
- relaying requests to Luna
- returning node, group, network, switch, BMC setup, OS image, and cloud data to the frontend

## Technology stack

- Vue 3
- TypeScript
- Vite
- Open OnDemand integration through Flask and Passenger
- Luna node backend through `/api/v1`

## Project structure

```text
.
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── env.d.ts
├── public/
│   ├── icons/
│   ├── img/
│   └── vendor/
└── src/
    ├── main.ts
    ├── App.vue
    ├── api.ts
    ├── assets/
    │   ├── styles.css
    │   └── group-ui-align.css
    ├── components/
    │   ├── AppHeader.vue
    │   ├── AppFooter.vue
    │   ├── BaseModal.vue
    │   ├── NodeInventory.vue
    │   ├── NodeFormFields.vue
    │   ├── InterfaceRow.vue
    │   ├── AddNodeModal.vue
    │   ├── EditNodeModal.vue
    │   ├── CloneNodeModal.vue
    │   ├── DeleteNodeModal.vue
    │   ├── NodePushFlowModal.vue
    │   └── TextEditorModal.vue
    ├── constants/
    │   └── displayName.ts
    ├── types/
    │   └── index.ts
    └── utils/
        ├── assetImg.ts
        ├── nextFreeIpv4.ts
        ├── nodeInterfaces.ts
        └── publicAssets.ts
```

## Main components

### `App.vue`

Top-level application shell. It owns modal state and connects the inventory table to the action dialogs.

It opens and closes:

- add node modal
- edit node modal
- clone node modal
- delete node modal
- OS Grab / OS Push modal

It also refreshes the inventory table after successful changes.

### `NodeInventory.vue`

Main node table.

Responsibilities:

- load node data from the backend
- display node inventory fields
- search nodes
- sort visible columns
- paginate results
- show interface data
- open actions for edit, clone, OS Grab, OS Push, and delete
- collect existing IPv4 records for the next-free-IP helper

### `NodeFormFields.vue`

Shared node form used by add, edit, and clone flows.

Responsibilities:

- render common node fields
- render advanced fields
- render interfaces through `InterfaceRow.vue`
- hydrate the form from backend data
- build the Luna node record payload
- track removed interfaces
- support inline rename during edit
- handle script and long text fields
- show source labels for inherited values

### `InterfaceRow.vue`

Single interface row inside the node form.

Responsibilities:

- edit interface name
- select network
- edit IP address
- suggest next free IPv4 address
- edit MAC address
- edit MTU
- toggle DHCP
- edit bond settings
- edit VLAN settings
- edit interface options
- add or remove interface rows

In clone mode, the component can prefill the next free IP address so that the cloned node does not reuse the source node IP.

### `AddNodeModal.vue`

Create-node workflow.

It loads option lists, validates the node name, builds a node record, and calls the add endpoint.

### `EditNodeModal.vue`

Update-node workflow.

It loads the selected node, tracks the initial snapshot, detects whether anything changed, handles node rename, removes deleted interfaces, and calls the update endpoint.

### `CloneNodeModal.vue`

Clone-node workflow.

It loads source node data, lets the user provide a new clone name, adjusts interface values, and calls the clone endpoint.

### `DeleteNodeModal.vue`

Delete-node confirmation workflow.

It confirms the node name and calls the delete endpoint.

### `NodePushFlowModal.vue`

Shared modal for OS Grab and OS Push.

For OS Grab it can submit:

- selected node
- OS image
- bare option
- nodry option

For OS Push it can submit:

- selected node
- OS image
- nodry option

### `TextEditorModal.vue`

Larger editor for long text fields.

Used for fields such as:

- kernel options
- pre script
- part script
- post script
- comment
- interface options

## API layer

All frontend API access is centralised in:

```text
src/api.ts
```

The frontend uses `/api/v1` endpoints exposed by the Flask backend.

Important API operations include:

```text
GET    /api/v1/node
GET    /api/v1/node/<name>
POST   /api/v1/add
POST   /api/v1/update/<name>
POST   /api/v1/rename
POST   /api/v1/clone
DELETE /api/v1/delete/<name>
GET    /api/v1/remove-interface/<node>/<interface>
POST   /api/v1/ospush/<node>
POST   /api/v1/osgrab/<node>
GET    /api/v1/resource/<table>
```

The exact route implementation lives in the Flask backend.

## Backend relationship

This frontend expects the Flask backend to provide:

- node records
- node form option lists
- group list
- switch list
- BMC setup list
- OS image list
- network list
- cloud list
- node add, update, rename, clone, delete operations
- interface removal
- OS Grab and OS Push operations

The backend response format is normalised in `src/api.ts`.

The frontend can unwrap backend responses shaped like:

```json
{
  "status": true,
  "status_code": 200,
  "content": {}
}
```

It can also handle direct JSON content when the backend returns already-unwrapped data.

## Environment variables

### Development

Create `.env.development` when running the frontend locally:

```env
VITE_NODE_BACKEND=https://your-ood-host/pun/sys/trinity_node
```

During development, Vite uses the `/node-backend` proxy. The frontend calls `/node-backend/api/v1/...`, and Vite forwards those requests to `VITE_NODE_BACKEND`.

The proxy is configured in `vite.config.ts`:

```text
/node-backend -> VITE_NODE_BACKEND
```

### Production

Production uses `VITE_PUBLIC_BASE` to control where the built assets are loaded from.

Example:

```env
VITE_PUBLIC_BASE=/pun/sys/trinity_node/assets/
```

Set this value to the URL path where the Flask Open OnDemand app serves the frontend build assets.

Important: this path must match the Flask app static path. If the Flask backend serves assets from `/pun/sys/trinity_node/app/assets/`, use that path instead. If it serves assets from `/pun/sys/trinity_node/assets/`, use that path.

## Install dependencies

```bash
npm install
```

## Run in development

```bash
npm run dev
```

The default Vite development server runs on:

```text
http://localhost:5173
```

When using the backend proxy, ensure `.env.development` contains `VITE_NODE_BACKEND`.

Example:

```env
VITE_NODE_BACKEND=https://controller.example.cluster/pun/sys/trinity_node
```

Then start the dev server:

```bash
npm run dev
```

## Type checking

```bash
npm run type-check
```

Run this before committing or building for production.

## Build

```bash
npm run build
```

The production build is generated in:

```text
dist/
```

The Vite config uses stable output names:

```text
dist/index.js
dist/index.css
```

Other assets are emitted with their original asset names.

## Production deployment flow

Typical deployment flow:

```bash
npm install
npm run type-check
npm run build
```

Then copy the contents of `dist/` into the static asset directory used by the Flask backend in the `trinityx-ood` repository.

Example layout on the backend side may look like:

```text
trinityx-ood/
└── node/
    ├── app.py
    ├── passenger_wsgi.py
    └── app/
        └── assets/
            ├── index.js
            ├── index.css
            ├── icons/
            ├── img/
            └── vendor/
```

The exact target directory depends on how the Flask app is configured. The key rule is:

```text
VITE_PUBLIC_BASE must match the URL path used by Flask to serve the built assets.
```

## Open OnDemand and Passenger

In production, this frontend is not served by Vite.

The expected production chain is:

```text
Open OnDemand
  -> Passenger
    -> Flask node backend from trinityx-ood
      -> serves Vue build assets
      -> exposes /api/v1 backend routes
```

Because the app runs under Open OnDemand, URLs are usually mounted under a path like:

```text
/pun/sys/trinity_node/
```

Do not assume the app is mounted at `/`. Use `VITE_PUBLIC_BASE` for production asset paths.

## Development versus production URLs

### Development

Frontend:

```text
http://localhost:5173
```

Backend proxy:

```text
/node-backend/api/v1/...
```

The proxy target comes from:

```text
VITE_NODE_BACKEND
```

### Production

Frontend and backend are served from the same Open OnDemand Passenger app.

API base is derived from the current page URL and then `/api/v1` is appended.

Example:

```text
https://ood.example.cluster/pun/sys/trinity_node/api/v1/node
```

## Node fields

The form supports Luna node fields including:

- `name`
- `group`
- `osimage`
- `osimagetag`
- `kerneloptions`
- `vendor`
- `assettag`
- `switch`
- `switchport`
- `cloud`
- `setupbmc`
- `bmcsetup`
- `unmanaged_bmc_users`
- `netboot`
- `service`
- `roles`
- `scripts`
- `prescript`
- `partscript`
- `postscript`
- `provision_interface`
- `provision_method`
- `provision_fallback`
- `tpm_uuid`
- `tpm_pubkey`
- `tpm_sha256`
- `comment`
- `newnodename`

Some frontend field names are mapped to Luna/backend names before submission:

```text
groupname      -> group
bmcsetupname   -> bmcsetup
switchname     -> switch
asset_tag      -> assettag
cloud_name     -> cloud
```

## Interface fields

Each node can have zero or more interfaces.

Supported interface fields include:

- `interface`
- `network`
- `ipaddress`
- `macaddress`
- `mtu`
- `dhcp`
- `bond_mode`
- `bond_slaves`
- `vlanid`
- `vlan_parent`
- `options`

## Script and editor fields

The following fields are treated as editor-style fields:

- `options`
- `content`
- `comment`
- `prescript`
- `partscript`
- `postscript`
- `grab_filesystems`
- `grab_exclude`
- `kerneloptions`

These fields may contain long text, scripts, comments, or multi-line values.

Before sending to the backend, editor-style fields are base64 encoded in `src/api.ts`. When node records are loaded, these fields are decoded where possible.

This is important for script fields because Luna may expect encoded script content.

## Clearing scripts

For edit mode, clearing a script field must be sent explicitly. If the field is simply omitted from the update payload, Luna may keep the existing value or fall back to an inherited value.

The frontend handles clearable script fields:

- `prescript`
- `partscript`
- `postscript`

When these fields are cleared, the frontend sends an explicit empty value so the backend can clear the node-level override.

## Source labels and inheritance

Luna node data may include source metadata fields such as:

```text
_kerneloptions_source
_prescript_source
_partscript_source
_postscript_source
_setupbmc_source
_netboot_source
_osimage_source
_bmcsetup_source
```

The frontend can display these as labels such as:

```text
NODE
GROUP
OS IMAGE
DEFAULT
```

These labels help the user understand whether a value is directly set on the node or inherited from another layer.

Practical meaning:

- `NODE`: the value is set directly on this node
- `GROUP`: the value is inherited from the node group
- `OS IMAGE`: the value is inherited from the OS image
- `DEFAULT`: the value comes from a Luna default

If a cleared value appears again after reload, it may be inherited rather than still set on the node.

## OS Grab

OS Grab captures the state of a node into an OS image.

The frontend supports:

- target node
- OS image
- bare option
- nodry option

The request is submitted to:

```text
POST /api/v1/osgrab/<node>
```

Use OS Grab when a node has been prepared and that state should be captured into an image.

## OS Push

OS Push deploys or synchronises an OS image to a node.

The frontend supports:

- target node
- OS image
- nodry option

The request is submitted to:

```text
POST /api/v1/ospush/<node>
```

Use OS Push when an OS image should be pushed to a node.

## Next free IP logic

The next free IPv4 helper is implemented in:

```text
src/utils/nextFreeIpv4.ts
```

It uses inventory data collected from the node table and the selected network to suggest the next free IPv4 address.

The GUI uses this for:

- manual `NEXT IP` button in interface rows
- clone mode IP prefill

Clone mode should avoid reusing the source node IP address.

## Validation and display names

Display-name and node-name validation helpers live in:

```text
src/constants/displayName.ts
```

They are used to:

- format names in headers and tables
- validate add node names
- validate clone node names
- validate rename values

## Assets

Static assets are stored in:

```text
public/
src/assets/
```

Common assets include:

- application logo
- action icons
- bundled Geist Sans font files
- CSS files

Vite copies assets from `public/` during build.

## Common commands

```bash
npm install
npm run dev
npm run type-check
npm run build
npm run preview
```

## Troubleshooting

### API calls fail in development

Check `.env.development`:

```env
VITE_NODE_BACKEND=https://your-ood-host/pun/sys/trinity_node
```

Restart `npm run dev` after changing the file.

### Production page loads but CSS or JS is missing

Check `VITE_PUBLIC_BASE`.

It must match the path where Flask serves the built assets.

Examples:

```env
VITE_PUBLIC_BASE=/pun/sys/trinity_node/assets/
```

or:

```env
VITE_PUBLIC_BASE=/pun/sys/trinity_node/app/assets/
```

Use the one that matches the backend Flask `static_url_path`.

### Page works in development but not in Open OnDemand

Confirm:

- `npm run build` was run
- `dist/` contents were copied to the Flask backend static directory
- Passenger app was restarted if needed
- `VITE_PUBLIC_BASE` matches the Open OnDemand mount path
- Flask backend routes are available under `/api/v1`

### A cleared field appears again

The value may be inherited from group, OS image, or default configuration. Check the source label. If it shows `GROUP`, `OS IMAGE`, or `DEFAULT`, the value is not necessarily set directly on the node.

### A cloned node gets the wrong IP

Check:

- selected network on the interface
- existing inventory IP records
- whether the source node is excluded correctly
- whether the IP is already assigned to another node
- whether the interface was manually changed after clone prefill

### TypeScript complains about literal types

For strict props such as:

```ts
flow: 'ospush' | 'osgrab'
```

make sure refs are typed as the same union type rather than plain `string`.

Example:

```ts
type PushFlowType = 'ospush' | 'osgrab'

const pushFlowType = ref<PushFlowType | ''>('')
```

## Coding notes

- Keep API access in `src/api.ts`.
- Keep shared form logic in `NodeFormFields.vue`.
- Keep interface-specific logic in `InterfaceRow.vue`.
- Keep modal-specific submit logic in the corresponding modal component.
- Avoid duplicating backend route construction outside `src/api.ts`.
- Run `npm run type-check` before committing.
- Run `npm run build` before copying assets into the backend repository.

## License

This project is part of the TrinityX software suite and is licensed under the GNU General Public License, version 3 or later.

See:

```text
LICENSE.txt
```

## Maintainer

```text
ClusterVision Solutions b.v.
Luna2 Project[OOD]
Maintainer: Yixin Zhang
Email: yixin.zhang@clustervision.com
Status: Development
```
