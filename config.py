import configparser
import os
import sys
config = configparser.ConfigParser()
config.read(os.path.join(sys.path[0] + "/config.ini"))
email = config['LOGIN']['email']
password = config['LOGIN']['password']
owner_id = config['OWNER']['id']
twitch_id = config['TWITCH']['client_id']
carbon_key = config['CARBON']['key']