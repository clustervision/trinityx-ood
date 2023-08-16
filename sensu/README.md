## Open OnDemand Passenger Sensu Dashboard

This is a [Flask](http://flask.pocoo.org/) application that polls the sensu/uchiwa json interface and serves the result in a minimal template
Intended to be run on passenger inside OpenOnDemand.

## Installation
This package requires `python3` and the python modules listed in the `requirements.txt` file
```
pip install -r requirements.txt
```
If you want to test the installation with passenger there's a a docker image available `phusion/passenger-full`

## Configuration
Configuration are located inside `settings.toml` where you can define the sensu endpoint and if OOD is running trough TLS or not. 

## Running
For debug run you can either run the entrypoint file directly
```
python3 app.py
```
Or run it trough flask
```
flask run --debug
```
In order to run it with passenger ( NOTE: it will read the Passengerfile.json )
```
passenger start
```
## Caveats
- Setting `ood_use_tls` inside `settings.toml` is a hacky workaround, but as for now it's not obvious how to programmatically gather this information.
- There is no documented approach to change the OOD `python` . Current approach is to symlink `/usr/bin/python3` to `/usr/bin/python`

## OOD Integration
In order to fully integrate this app inside OOD the following steps are required:
- Install `python3` and `python3-pip`
- [Optional] Create and activate a virtualenv
- Clone the repository to `/var/www/ood/apps/sys/`
- Install the python modules located inside `requirements.txt`
- Change the configuration settings inside `settings.toml`
- Make sure that `python` resolves to the correct interpreter (`/usr/bin/python3` if no virtualenv has been activated) in order to allow OOD to start the flask server
