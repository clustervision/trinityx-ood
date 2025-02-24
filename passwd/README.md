## PASSWD

This project will serve the PASSWD application which is tide up with the Luna for Trinity Project.

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
- This application will help user to change the password
- mkdir /etc/ood/config/apps/dashboard
- vim /etc/ood/config/apps/dashboard/env
- ADD --> OOD_DASHBOARD_PASSWD_URL=/pun/sys/trinityx_passwd
- systemctl restart httpd.service nginx.service
- Open Browser & Go To: https://controller1:8080/pun/sys/trinityx_passwd
