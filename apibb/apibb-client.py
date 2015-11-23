
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
import click

# import from the 21 Developer Library
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

# set up bitrequest client for BitTransfer requests
wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)

APIBBCLI_VERSION = '0.1'
DEFAULT_ENDPOINT = 'http://localhost:12002/'

@click.group()
@click.option('--endpoint', '-e',
              default=DEFAULT_ENDPOINT,
              metavar='STRING',
              show_default=True,
              help='API endpoint URI')
@click.option('--debug', '-d',
              is_flag=True,
              help='Turns on debugging messages.')
@click.version_option(APIBBCLI_VERSION)
@click.pass_context
def main(ctx, endpoint, debug):
    """ Command-line Interface for the API bulletin board service
    """

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj['endpoint'] = endpoint

@click.command(name='info')
@click.pass_context
def cmd_info(ctx):
    sel_url = ctx.obj['endpoint']
    answer = requests.get(url=sel_url.format())
    print(answer.text)

@click.command(name='names')
@click.pass_context
def cmd_get_names(ctx):
    sel_url = ctx.obj['endpoint'] + 'names'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

@click.command(name='namerenew')
@click.argument('name')
@click.argument('hours')
@click.pass_context
def cmd_name_renew(ctx, name, hours):
    sel_url = ctx.obj['endpoint'] + 'namerenew?name={0}&hours={1}'
    answer = requests.get(url=sel_url.format(name, hours))
    print(answer.text)

@click.command(name='ads')
@click.argument('name')
@click.pass_context
def cmd_get_ads(ctx, name):
    sel_url = ctx.obj['endpoint'] + 'ads?name={0}'
    answer = requests.get(url=sel_url.format(name))
    print(answer.text)

@click.command(name='post.ad')
@click.argument('name')
@click.argument('uri')
@click.argument('pubkey')
@click.argument('hours')
@click.pass_context
def cmd_advertise(ctx, name, uri, pubkey, hours):
    sel_url = ctx.obj['endpoint'] + 'advertise?name={0}&uri={1}&pubkey={2}&hours={3}'
    answer = requests.get(url=sel_url.format(name, uri, pubkey, hours))
    print(answer.text)

main.add_command(cmd_info)
main.add_command(cmd_name_renew)
main.add_command(cmd_get_names)
main.add_command(cmd_get_ads)
main.add_command(cmd_advertise)

if __name__ == "__main__":
    main()

