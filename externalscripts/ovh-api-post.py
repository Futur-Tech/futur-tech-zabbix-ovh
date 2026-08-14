#!/usr/bin/python3

# -*- encoding: utf-8 -*-

# Usage: /usr/lib/zabbix/externalscripts/ovh-api-post.py <conf_name (without .conf)> <api_path>
# Example:
# /usr/lib/zabbix/externalscripts/ovh-api-post.py default_api /email/domain/test.fr/account/test/updateUsage ## Request quota update for email test@test.fr
# /usr/lib/zabbix/externalscripts/ovh-api-post.py default_api /v2/zimbra/platform/00000000-0000-0000-0000-000000000000/refreshQuotaUsage ## Request quota update for a whole Zimbra platform


import sys
import json
import ovh
import configparser
import os.path

conf_name = str(sys.argv[1])
api_path = str(sys.argv[2])

conf_path = str('/usr/local/etc/futur-tech-zabbix-ovh/' + conf_name + '.conf')

if not os.path.exists(conf_path):
    print('Config file not found: ' + conf_path)
    exit()

# Load the config
config = configparser.ConfigParser()
config.read(conf_path)

# Instanciate an OVH Client.
# You can generate new credentials with full access to your account on
# the token creation page https://api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*
client = ovh.Client(
    endpoint=config['OVH_API']['endpoint'],               # Endpoint of API OVH (List of available endpoints https://github.com/ovh/python-ovh#2-configure-your-application)
    application_key=config['OVH_API']['application_key'],    # Application Key
    application_secret=config['OVH_API']['application_secret'], # Application Secret
    consumer_key=config['OVH_API']['consumer_key'],       # Consumer Key
)

# Routing a /v1 or /v2 path to the right base URL is done by python-ovh >= 1.1.0 only
if api_path.startswith('/v2/') and not hasattr(client, '_get_target'):
    print('The installed python-ovh module does not support OVH API v2, run: pip3 install -U ovh --break-system-packages')
    exit(1)

try:
    result = client.post(api_path)
except ovh.exceptions.InvalidResponse:
    # Some API v2 calls (i.e. /v2/zimbra/platform/{platformId}/refreshQuotaUsage) answer with an
    # empty body which python-ovh cannot decode. Nothing returned means nothing went wrong.
    result = None

# Pretty print
print(json.dumps(result, indent=4))