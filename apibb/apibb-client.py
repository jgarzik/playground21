
#
# Command line usage:
# $ python3 apibb-client.py
# $ python3 apibb-client.py namerenew NAME EXPIRE-HOURS
# $ python3 apibb-client.py get.ads NAME
# $ python3 apibb-client.py post.ad NAME URI PUBKEY EXPIRE-HOURS
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
server_url = 'http://localhost:12002/'

def cmd_info():
    sel_url = server_url + 'info'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

def cmd_get_ads(name):
    sel_url = server_url + 'ads?name={0}'
    answer = requests.get(url=sel_url.format(name))
    print(answer.text)

def cmd_get_names():
    sel_url = server_url + 'names'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

def cmd_name_renew(name, hours):
    sel_url = server_url + 'namerenew?name={0}&hours={1}'
    answer = requests.get(url=sel_url.format(name, hours))
    print(answer.text)

def cmd_advertise(name, uri, pubkey, hours):
    sel_url = server_url + 'advertise?name={0}&uri={1}&pubkey={2}&hours={3}'
    answer = requests.get(url=sel_url.format(name, uri, pubkey, hours))
    print(answer.text)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc == 1:
        cmd_info()
    elif sys.argv[1] == "namerenew" and argc == 4:
        cmd_name_renew(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "names" and argc == 2:
        cmd_get_names()
    elif sys.argv[1] == "ads" and argc == 3:
        cmd_get_ads(sys.argv[2])
    elif sys.argv[1] == "post.ad" and argc == 6:
        cmd_advertise(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print("invalid command line usage")

