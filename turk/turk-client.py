
#
# Command line usage:
# $ python3 turk-client.py --help
#

import json
import os
import sys
import click
import binascii
import time
import pprint

import worktmp
import util

# import from the 21 Developer Library
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

pp = pprint.PrettyPrinter(indent=2)

# set up bitrequest client for BitTransfer requests
wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)

TURKCLI_VERSION = '0.1'
DEFAULT_ENDPOINT = 'http://localhost:12007/'

@click.group()
@click.option('--endpoint', '-e',
              default=DEFAULT_ENDPOINT,
              metavar='STRING',
              show_default=True,
              help='API endpoint URI')
@click.option('--debug', '-d',
              is_flag=True,
              help='Turns on debugging messages.')
@click.version_option(TURKCLI_VERSION)
@click.pass_context
def main(ctx, endpoint, debug):
    """ Command-line Interface for the Mechanical turk API service
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

@click.command(name='submit.task')
@click.argument('id')
@click.argument('pkh')
@click.argument('answersfile', type=click.File('r'))
@click.pass_context
def cmd_task_submit(ctx, id, pkh, answersfile):
    try:
        answers_obj = json.load(answersfile)
    except:
        print("Unable to decode JSON work answers")
        sys.exit(1)

    tstamp = int(time.time())
    req_obj = {
        'pkh': pkh,
        'id': id,
        'tstamp': tstamp,
        'answers': answers_obj,
    }

    body = json.dumps(req_obj)

    sig_str = wallet.sign_bitcoin_message(body, pkh)
    if not wallet.verify_bitcoin_message(body, sig_str, pkh):
        print("Error: cannot self-verify signed message")
        sys.exit(1)

    sel_url = ctx.obj['endpoint'] + 'task'
    headers = {
        'Content-Type': 'application/json',
        'X-Bitcoin-Sig': sig_str,
    }
    answer = requests.post(url=sel_url.format(), headers=headers, data=body)
    print(answer.text)

@click.command(name='get.task')
@click.argument('id')
@click.argument('pkh')
@click.pass_context
def cmd_task_get(ctx, id, pkh):
    # Build, hash and sign pseudo-header
    tstamp = int(time.time())
    msg = util.hash_task_phdr(id, pkh, tstamp)
    sig_str = wallet.sign_bitcoin_message(msg, pkh)
    if not wallet.verify_bitcoin_message(msg, sig_str, pkh):
        print("Error: cannot self-verify signed message")
        sys.exit(1)

    # Send request to endpoint
    sel_url = ctx.obj['endpoint'] + 'task/' + id
    headers = {
        'X-Bitcoin-PKH': pkh,
        'X-Bitcoin-Sig': sig_str,
        'X-Timestamp': str(tstamp),
    }
    answer = requests.get(url=sel_url.format(), headers=headers)
    print(answer.text)

@click.command(name='tasklist')
@click.pass_context
def cmd_task_list(ctx):
    sel_url = ctx.obj['endpoint'] + 'tasks.list'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

@click.command(name='new.task')
@click.argument('summary')
@click.argument('imagefile', type=click.File('rb'))
@click.argument('content_type')
@click.argument('templatefile', type=click.File('r'))
@click.argument('min_workers')
@click.argument('reward')
@click.pass_context
def cmd_task_new(ctx, summary, imagefile, content_type, templatefile, min_workers, reward):
    try:
        template_obj = json.load(templatefile)
    except:
        print("Unable to decode JSON work template")
        sys.exit(1)

    wt = worktmp.WorkTemplate()
    wt.set(template_obj)
    if not wt.valid():
        print("JSON work template not valid")
        sys.exit(1)

    auth_pubkey = wallet.get_message_signing_public_key()
    auth_pkh = auth_pubkey.address()

    print("Registering as supervisor pubkey " + auth_pkh)

    req_obj = {
        'pkh': auth_pkh,
        'summary': summary,
        'image': binascii.hexlify(imagefile.read()).decode('utf-8'),
        'image_ctype': content_type,
        'template': template_obj,
        'min_workers': int(min_workers),
        'reward': int(reward),
    }

    body = json.dumps(req_obj)

    sel_url = ctx.obj['endpoint'] + 'task.new'
    headers = { 'Content-Type': 'application/json', }
    answer = requests.post(url=sel_url.format(), headers=headers, data=body)
    print(answer.text)

@click.command(name='register')
@click.pass_context
def cmd_register(ctx):
    auth_pubkey = wallet.get_message_signing_public_key()
    auth_pkh = auth_pubkey.address()

    print("Registering as worker pubkey " + auth_pkh)

    req_obj = {
        'pkh': auth_pkh,
        'payout_addr': wallet.get_payout_address(),
    }

    body = json.dumps(req_obj)

    sel_url = ctx.obj['endpoint'] + 'worker.new'
    headers = { 'Content-Type': 'application/json', }
    answer = requests.post(url=sel_url.format(), headers=headers, data=body)
    print(answer.text)

main.add_command(cmd_info)
main.add_command(cmd_task_new)
main.add_command(cmd_task_get)
main.add_command(cmd_task_submit)
main.add_command(cmd_task_list)
main.add_command(cmd_register)

if __name__ == "__main__":
    main()

