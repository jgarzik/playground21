
#
# Command line usage:
# $ python3 kvram-client.py		# Get service info (JSON)
# $ python3 kvram-client.py KEY		# Get value from server, given KEY
# $ python3 kvram-client.py KEY VALUE	# Store KEY and VALUE on server
#

import json
import os
import sys

# import from the 21 Developer Library
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

# set up bitrequest client for BitTransfer requests
wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)

# server address
server_url = 'http://localhost:12001/'

def cmd_get(key):
    sel_url = server_url + 'get?key={0}'
    answer = requests.get(url=sel_url.format(key))
    print(answer.text)

def cmd_put(key, value):
    sel_url = server_url + 'put?key={0}&value={1}'
    answer = requests.get(url=sel_url.format(key, value))
    print(answer.text)

def cmd_info():
    sel_url = server_url + 'info'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        cmd_get(sys.argv[1])
    elif len(sys.argv) == 3:
        cmd_put(sys.argv[1], sys.argv[2])
    else:
        cmd_info()

