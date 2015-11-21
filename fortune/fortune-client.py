#!/usr/bin/python3

#
# Command line usage:
# $ python3 fortune-client.py		# Get pithy saying
# $ python3 fortune-client.py info	# Get server metadata
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
server_url = 'http://localhost:12012/'

def cmd_fortune():
    sel_url = server_url
    answer = requests.get(url=sel_url.format())
    print(answer.text)

def cmd_info():
    sel_url = server_url + 'info'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "info":
        cmd_info()
    else:
        cmd_fortune()

