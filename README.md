# OVH Monitoring with Zabbix
Monitoring of OVH account (domains, emails etc...)

Works for Zabbix 6.0 Server

## What it does
- Monitoring of Domain Names
- Monitoring of Email Accounts (MX Plan / Email Pro, OVH API v1)
- Monitoring of Zimbra Email Accounts (OVH API v2)
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

1. Edit `/usr/local/etc/futur-tech-zabbix-ovh/template_api.conf` with your API key details
1. Rename `template_api.conf` to `some_name.conf`
1. Import the template XML in Zabbix Server
1. Create a new host and link **Template Futur-Tech OVH API**  
1. Override the macro `{$OVH_API_CONF_NAME}` with the conf file name (without the **.conf**)

## Multiple OVH Account Monitoring
You can monitor several OVH API conf, create one Zabbix host for each.

## Zimbra
Zimbra is served by the **OVH API v2**, which the scripts detect from the `/v2/` prefix of the path. Two things differ from the v1 API and are handled transparently:

- Lists are paginated with a cursor, `ovh-api-get.py` follows it until the last page.
- Lists return objects instead of plain strings, so a 4th argument tells `ovh-api-get.py` which key of those objects to loop on (always `id` for v2 resources).

Requirements:

- `python-ovh` **1.1.0 or later** (`deploy.sh` installs it with `pip3 install -U ovh`). Older versions cannot route a `/v2/` path and the items will report it.
- The API token needs `GET` and `POST` on `/v2/zimbra/*`.

The template discovers Zimbra platforms and, for every platform, all of its email accounts. It monitors the space used and total, the account status and whether OVH has blocked the account (spam or unpaid slot).

OVH does not compute the space used in real time: the template periodically calls `/v2/zimbra/platform/{platformId}/refreshQuotaUsage` to ask for a recomputation, and triggers if that request fails or if the reported figures grow stale.

Two details of the API v2 payload worth knowing:

- Quota values are in bytes (a PRO account reports `53687091200`, i.e. 50 GiB).
- `quota.available` is the space **left**, not the size of the account. The item *space total* maps to `quota.maximum`.

## Testing OVH API
From Zabbix Server you can test API calls

```bash
## This will list email domains
/usr/lib/zabbix/externalscripts/ovh-api-get.py template_api /email/domain

## This will return a JSON with all email accounts for each email domain
/usr/lib/zabbix/externalscripts/ovh-api-get.py template_api /email/domain /email/domain/#loop#/account

## Request quota update for email test@test.fr
/usr/lib/zabbix/externalscripts/ovh-api-post.py template_api /email/domain/test.fr/account/test/updateUsage

## This will list Zimbra platforms
/usr/lib/zabbix/externalscripts/ovh-api-get.py template_api /v2/zimbra/platform

## This will return a JSON with all Zimbra accounts for each Zimbra platform
/usr/lib/zabbix/externalscripts/ovh-api-get.py template_api /v2/zimbra/platform /v2/zimbra/platform/#loop#/account id

## Request quota usage update for a whole Zimbra platform (answers "null" when it worked)
/usr/lib/zabbix/externalscripts/ovh-api-post.py template_api /v2/zimbra/platform/<platformId>/refreshQuotaUsage
```

## Note
This is my first Python script... if you can do better, feel free to make a pull request.

## Credits
OVH Python: https://github.com/ovh/python-ovh