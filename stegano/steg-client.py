#!/usr/bin/python3

#
# Command line usage:
# $ python3 steg-client.py --help
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

STEGCLI_VERSION = '1.0'
DEFAULT_ENDPOINT = 'http://localhost:12018/'

@click.group(invoke_without_command=True)
@click.option('--endpoint', '-e',
              default=DEFAULT_ENDPOINT,
              metavar='STRING',
              show_default=True,
              help='API endpoint URI')
@click.option('--debug', '-d',
              is_flag=True,
              help='Turns on debugging messages.')
@click.version_option(STEGCLI_VERSION)
@click.pass_context
def main(ctx, endpoint, debug):
    """ Command-line Interface for the steganography service
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


@click.command(name='encode')
@click.argument('message', type=click.File('rb'))
@click.argument('file', type=click.File('rb'))
@click.pass_context
def cmd_encode(ctx, message, file):
    sel_url = ctx.obj['endpoint'] + 'encode'
    files = { 'message': message, 'file': file }
    answer = requests.post(url=sel_url.format(), files=files)
    print(answer.text)


@click.command(name='decode')
@click.argument('file', type=click.File('rb'))
@click.pass_context
def cmd_decode(ctx, file):
    sel_url = ctx.obj['endpoint'] + 'decode'
    files = { 'file': file }
    answer = requests.post(url=sel_url.format(), files=files)
    print(answer.text)


main.add_command(cmd_info)
main.add_command(cmd_encode)
main.add_command(cmd_decode)

if __name__ == "__main__":
    main()

