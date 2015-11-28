
#
# Command line usage:
# $ python3 dns-client.py --help
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

DNSCLI_VERSION = '0.1'
DEFAULT_ENDPOINT = 'http://localhost:12005/'

@click.group()
@click.option('--endpoint', '-e',
              default=DEFAULT_ENDPOINT,
              metavar='STRING',
              show_default=True,
              help='API endpoint URI')
@click.option('--debug', '-d',
              is_flag=True,
              help='Turns on debugging messages.')
@click.version_option(DNSCLI_VERSION)
@click.pass_context
def main(ctx, endpoint, debug):
    """ Command-line Interface for the DDNS API service
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

@click.command(name='domains')
@click.pass_context
def cmd_domains(ctx):
    sel_url = ctx.obj['endpoint'] + 'domains'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

main.add_command(cmd_info)
main.add_command(cmd_domains)

if __name__ == "__main__":
    main()

