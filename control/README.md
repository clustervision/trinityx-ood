## Control Manager

This project will serve the Control APPS which is tide up with the Luna for Trinity Project.

## Installation
This package requires `python3.10` and the python modules listed in the `requirements.txt` file
```
pip install -r requirements.txt
```

## Integration
In order to fully integrate this app inside OOD the following steps are required:
- Install `python3` and `python3-pip`
- Clone the repository to `/var/www/ood/apps/sys/`
- Install the python modules located inside `requirements.txt`

## Frontend (Vue SPA)
The UI is built from the separate `control` repository (Vite + Vue), not from `static/` or `templates/` in this tree.

```bash
cd control && npm ci && npm run build
# Deploy dist/index.js and dist/index.css into app/assets/ on the controller
```

Flask serves the SPA shell from `app/index.html` and static files from `app/assets/` (`static_url_path=/app/assets`).

Copy the logo from the frontend build: `control/public/img/logo.png` → `app/assets/img/logo.png` (deploy `dist/img/` with `dist/index.js` and `dist/index.css`).
