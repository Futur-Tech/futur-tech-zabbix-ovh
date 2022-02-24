#!/usr/bin/python3

# -*- encoding: utf-8 -*-

# Usage: /usr/local/bin/futur-tech-zabbix-ovh/ovh-api-get.py <conf_name (without .conf)> <api_path> <loop_api_path>
# <loop_api_path> Should be used when the <api_path> return a list which should be looped through replacing #loop#
# Example:
# /usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /email/domain ## This will list email domains
# /usr/lib/zabbix/externalscripts/ovh-api-get.py default_api /email/domain /email/domain/#loop#/account ## This will return a JSON with all email accounts for each email domain


import sys
import json
import ovh
import configparser
import os.path

conf_name = str(sys.argv[1])
api_path = str(sys.argv[2])

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
    endpoint=config['OVH_API']['endpoint'],               # Endpoint of API OVH Europe (List of available endpoints https://github.com/ovh/python-ovh#2-configure-your-application)
    application_key=config['OVH_API']['application_key'],    # Application Key
    application_secret=config['OVH_API']['application_secret'], # Application Secret
    consumer_key=config['OVH_API']['consumer_key'],       # Consumer Key
)

result = client.get(api_path)

# Check if need to loop through the result
if len(sys.argv)>3:
    loop_api_path=str(sys.argv[3])
    result_loop = []
    for value in result:
        result_loop_tmp = client.get(loop_api_path.replace("#loop#", str(value)))
        for value_tmp in result_loop_tmp:
            result_dict = {"source_result" : value, "loop_result" : value_tmp}
            result_loop.append(result_dict)
            
    # Now we replace previous results by our new results        
    result=result_loop

# Pretty print
print(json.dumps(result, indent=4))