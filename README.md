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

## Development mode
Every app with a `frontend/` folder can run against its live frontend, so backend and frontend changes reload without a build.
1. In the app's `constant.py`, set `APP_STATE = False`. Do not commit it: the pipeline rejects `APP_STATE = False`.
2. On the controller, as root, from the app's folder:
   ```
   /trinity/local/python/bin/python3 app.py
   ```
3. Open `http://<controller-ip>:7755/` (nodeboot: port 7756).

`devserver.py` starts the app's Vite dev server on port 5173 and runs Flask in debug mode. The page Flask renders loads the frontend from Vite instead of `app/assets/index.js`. `Ctrl+C` stops both.

- The first start runs `npm ci`, and again whenever `package-lock.json` changes. The controller needs Node.js 20.19 or later.
- On a VMware shared folder (`/mnt/hgfs`), `node_modules` is bind-mounted from `~/.cache/trinityx-ood-dev/<app>/` on the controller's own disk, because the shared folder cannot hold symlinks and its `node_modules` belongs to the host's OS. Vite polls for changes, as edits made on the host raise no file events in the VM.
- The browser must reach ports 7755 and 5173: `firewall-cmd --permanent --add-port=5173/tcp && firewall-cmd --reload`.
- Run one app at a time: Vite always uses port 5173.
- Flask's own messages, such as reloads and the debugger PIN, go to `/var/log/luna/luna2-web.log`.
