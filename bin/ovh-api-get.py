#!/usr/bin/python3

# -*- encoding: utf-8 -*-

# Usage: /usr/local/bin/futur-tech-zabbix-ovh/ovh-api-get.py <conf_name (without .conf)> <api_path>

import sys
import json
import ovh
import configparser
import os.path

conf_name = str(sys.argv[1])
api_path = str(sys.argv[2])

conf_path = str('/usr/local/etc/futur-tech-zabbix-ovh/' + conf_name + '.conf')

if not os.path.exists( conf_path ):
    print( 'Config file not found: ' + conf_path )
    exit()

# Load the config
config = configparser.ConfigParser()
config.read( conf_path )

# Instanciate an OVH Client.
# You can generate new credentials with full access to your account on
# the token creation page https://api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*
client = ovh.Client(
    endpoint=config['OVH_API']['endpoint'],               # Endpoint of API OVH Europe (List of available endpoints https://github.com/ovh/python-ovh#2-configure-your-application)
    application_key=config['OVH_API']['application_key'],    # Application Key
    application_secret=config['OVH_API']['application_secret'], # Application Secret
    consumer_key=config['OVH_API']['consumer_key'],       # Consumer Key
)

result = client.get( api_path )

# Pretty print
print(json.dumps(result, indent=4))