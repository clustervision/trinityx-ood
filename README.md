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
- Add required things to `/var/www/ood/apps/sys/`. Example ` cp -r /tmp/trinity-ood/bmcsetup /var/www/ood/apps/sys/`
- Install the python modules located inside `requirements.txt` in each module.
