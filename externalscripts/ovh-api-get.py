#!/usr/bin/python3

# -*- encoding: utf-8 -*-

# Usage: /usr/lib/zabbix/externalscripts/ovh-api-get.py <conf_name (without .conf)> <api_path> <loop_api_path> <loop_key>
# <loop_api_path> Should be used when the <api_path> return a list which should be looped through replacing #loop#
# <loop_key>      Should be used when <api_path> return a list of objects instead of a list of strings (OVH API v2).
#                 The value of that key is what replaces #loop# and what is reported as "source_result".
# Example:
# /usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /email/domain ## This will list email domains
# /usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /email/domain /email/domain/#loop#/account ## This will return a JSON with all email accounts for each email domain
# /usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /v2/zimbra/platform /v2/zimbra/platform/#loop#/account id ## This will return a JSON with all Zimbra accounts for each Zimbra platform


import sys
import json
import ovh
import configparser
import os.path

conf_name = str(sys.argv[1])
api_path = str(sys.argv[2])
loop_api_path = str(sys.argv[3]) if len(sys.argv) > 3 else None
loop_key = str(sys.argv[4]) if len(sys.argv) > 4 else None

conf_path = str('/usr/local/etc/futur-tech-zabbix-ovh/' + conf_name + '.conf')

if not os.path.exists(conf_path):
    print( 'Config file not found: ' + conf_path )
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
if (api_path.startswith('/v2/') or (loop_api_path or '').startswith('/v2/')) and not hasattr(client, '_get_target'):
    print( 'The installed python-ovh module does not support OVH API v2, run: pip3 install -U ovh --break-system-packages' )
    exit(1)


def api_get(path):
    """GET an API path, following the OVH API v2 cursor pagination if any.

    API v1 is not cursor paginated and is queried in a single call.
    https://docs.ovhcloud.com/en/guides/manage-and-operate/api/apiv2/
    """
    if not path.startswith('/v2/'):
        return client.get(path)

    paginated_result = []
    cursor = None

    while True:
        response = client.raw_call('GET', path, headers={'X-Pagination-Cursor': cursor} if cursor else None)

        if response.status_code >= 300:
            raise ovh.exceptions.APIError('HTTP ' + str(response.status_code) + ' on ' + path + ': ' + response.text)

        page = response.json() if response.content else None

        # Only lists are paginated, anything else is returned as-is
        if not isinstance(page, list):
            return page

        paginated_result += page

        # No cursor for a next page means the last page was reached
        cursor = response.headers.get('X-Pagination-Cursor-Next')
        if not cursor:
            return paginated_result


result = api_get(api_path)

# Check if need to loop through the result
if loop_api_path:
    result_loop = []
    for value in result:
        # With OVH API v2 the list holds objects, the loop value has to be read from one of their keys
        if loop_key:
            if not isinstance(value, dict) or value.get(loop_key) is None:
                continue
            value = value[loop_key]

        try:
            result_loop_tmp = api_get(loop_api_path.replace("#loop#", str(value)))
        except ovh.exceptions.APIError as e:
            # print(f"Error fetching data for {value}: {e}")
            continue

        for value_tmp in result_loop_tmp:
            result_dict = {"source_result": value, "loop_result": value_tmp}
            result_loop.append(result_dict)

    # Now we replace previous results by our new results
    result = result_loop

# Pretty print
print(json.dumps(result, indent=4))
