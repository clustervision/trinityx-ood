# Trinity Open On Demand

This project will fetch all the necessary information from Trinity tools and present it in the On Demand Dashboard as a separate application.

## Installation
This project requires `python3.10` and the python modules listed in the `requirements.txt` file in each submodule.
```
pip install -r requirements.txt
```

## Integration
In order to fully integrate this app inside OOD the following steps are required:
- Install `python3` and `python3-pip`
- Clone the repository to `/tmp/`
- Add required things to `/var/www/ood/apps/sys/`. Example ` cp -r /tmp/trinityx-ood/bmcsetup /var/www/ood/apps/sys/`
- Install the python modules located inside `requirements.txt` in each module.

## Packaging
CI builds one pip package that holds every app's backend together with its built frontend:
1. `frontend-build` reads `frontends.txt`. For each app listed there it runs `npm ci` and `npm run build` in `<app>/frontend/`, and copies the build into `<app>/app/assets/`.
2. `build-job` makes the pip package from the backend and the built assets. The `frontend/` folders are not part of it.
3. On `development` and `main`, `publish-job` uploads the package, and `frontend-publish` uploads each build as `<package>-1.0.latest.tar.gz`, the file older TrinityX installs download themselves.

`<app>/app/assets/` holds the committed build of each frontend. CI rebuilds it from `<app>/frontend/` on every pipeline, so the package always carries a fresh build. To keep the committed copy current, run `npm run build` in `<app>/frontend/` after a frontend change and copy `dist/` into `<app>/app/assets/`. A new frontend must be added to `frontends.txt`, or the pipeline fails.

## Development mode
Every app with a `frontend/` folder can run against its live frontend, so backend and frontend changes reload without a build.

You need a TrinityX controller with the OOD apps installed, because the app reads the controller's Luna configuration (`/trinity/local/ondemand/3.0/config/luna.ini`), plus Node.js 20.19 or later and npm on that controller.

1. In the app's `constant.py`, set `APP_STATE = False`. Do not commit it: the pipeline rejects `APP_STATE = False`.
2. On the controller, as root, from the app's folder in your checkout of this repository:
   ```
   /trinity/local/python/bin/python3 app.py
   ```
3. Open `http://<controller-ip>:7755/` (nodeboot: port 7756).

`devserver.py` starts the app's Vite dev server on port 5173 and runs Flask in debug mode. The page Flask renders loads the frontend from Vite instead of `app/assets/index.js`. `Ctrl+C` stops both.

- The first start runs `npm ci`, and again whenever `package-lock.json` changes.
- The browser must reach ports 7755 and 5173 on the controller. With firewalld: `firewall-cmd --permanent --add-port=7755/tcp --add-port=5173/tcp && firewall-cmd --reload`.
- Run one app at a time: Vite always uses port 5173.
- Flask's own messages, such as reloads and the debugger PIN, go to `/var/log/luna/luna2-web.log`.
