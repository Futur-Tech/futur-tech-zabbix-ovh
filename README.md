# OVH Monitoring with Zabbix
Monitoring of OVH account (domains, emails etc...)

Works for Zabbix 5.x Server

## What it does
- Monitoring of Domain Names
- Monitoring of Email Accounts
- Monitoring of Telephony Service Latest Registration
- Monitoring of OVH API keys

## Deployment
1. Create an API key for your OVH account [https://api.ovh.com/createToken/](https://api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*)

1. On the Zabbix Server:

    ```bash
    cd /usr/local/src
    git clone https://github.com/Futur-Tech/futur-tech-zabbix-ovh.git
    cd futur-tech-zabbix-ovh

    ./deploy.sh 
    # Main deploy script

    ./deploy-update.sh -b main
    # This script will automatically pull the latest version of the branch ("main" in the example) and relaunch itself if a new version is found. Then it will run deploy.sh. Also note that any additional arguments given to this script will be passed to the deploy.sh script.
    ```

1. Edit `/usr/local/etc/futur-tech-zabbix-ovh/default_api.conf` with your API key details
1. Import the template XML in Zabbix Server
1. Create a new host and link **Template Futur-Tech OVH API**  


## Multiple OVH Account Monitoring
1. Duplicate conf file `/usr/local/etc/futur-tech-zabbix-ovh/default_api.conf`
1. Rename it
1. Create a new host in Zabbix Server and overide the macre {$OVH_API_CONF_NAME} with the conf file name (without the **.conf**)

## Testing OVH API
From Zabbix Server you can test API calls

```bash
## This will list email domains
/usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /email/domain

## This will return a JSON with all email accounts for each email domain
/usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /email/domain /email/domain/#loop#/account

## Request quota update for email test@test.fr
/usr/lib/zabbix/externalscripts/ovh-api-post.py default_api /email/domain/test.fr/account/test/updateUsage
```

## Note
This is my first Python script... if you can do better, feel free to make a pull request.

## Credits
OVH Python: https://github.com/ovh/python-ovh