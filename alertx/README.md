## Alert configurator

This project will serve the Alert configurator which is tide up with the Luna for Trinity Project.

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

## Usage
- Most Important: This application is needed the read/write access for file /trinity/local/etc/prometheus_server/rules/trix.rules and needed permission to create/read/write file /trinity/local/etc/prometheus_server/rules/trix.rules.details
- Depends on the file: /trinity/local/etc/prometheus_server/rules/trix.rules
- It will create a new file called: /trinity/local/etc/prometheus_server/rules/trix.rules.details
- This Detailed version of file will hold the information about the Enabled or Disabled TRIX rules.
- With all detailed rule.
- Key: _trix_status Value: true or false
- This is just the detailed version of the actual trix.rules file.
- Whenever the application is open it is always add/edit the Detailed file.
- Ans depending on the _trix_status it will add remove the rules in the trix.rules(Main File)
