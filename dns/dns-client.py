
#
# Command line usage:
# $ python3 dns-client.py --help
#

import json
import os
import sys
import click
import pprint

# import from the 21 Developer Library
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

pp = pprint.PrettyPrinter(indent=2)

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
    sel_url = ctx.obj['endpoint'] + 'dns/1/domains'
    answer = requests.get(url=sel_url.format())
    print(answer.text)

@click.command(name='register')
@click.argument('name')
@click.argument('domain')
@click.argument('days')
@click.argument('recordlist', nargs=-1)
@click.pass_context
def cmd_register(ctx, name, domain, days, recordlist):

    pubkey = wallet.get_message_signing_public_key()
    addr = pubkey.address()
    print("Registering with key %s" % (addr,))

    records = []
    for arg in recordlist:
        words = arg.split(',')
        host_obj = {
            'ttl': int(words[0]),
            'rec_type': words[1],
            'address': words[2],
        }
        records.append(host_obj)

    req_obj = {
        'name': name,
        'domain': domain,
        'days': int(days),
        'pkh': addr,
        'hosts': records,
    }

    sel_url = ctx.obj['endpoint'] + 'dns/1/host.register'
    body = json.dumps(req_obj)
    headers = {'Content-Type': 'application/json'}
    answer = requests.post(url=sel_url.format(), headers=headers, data=body)
    print(answer.text)

@click.command(name='simpleregister')
@click.argument('name')
@click.argument('domain')
@click.argument('days')
@click.argument('ipaddress')
@click.pass_context
def cmd_simpleRegister(ctx, name, domain, days, ipaddress):
    sel_url = ctx.obj['endpoint'] + 'dns/1/simpleRegister?name={0}&domain={1}&days={2}&ip={3}'
    answer = requests.get(url=sel_url.format(name, domain, days, ipaddress))
    print(answer.text)

@click.command(name='update')
@click.argument('name')
@click.argument('domain')
@click.argument('pkh')
@click.argument('records', nargs=-1)
@click.pass_context
def cmd_update(ctx, name, domain, pkh, records):
    req_obj = {
        'name': name,
        'domain': domain,
        'hosts': [],
    }
    for record in records:
        words = record.split(',')
        host_obj = {
            'ttl': int(words[0]),
            'rec_type': words[1],
            'address': words[2],
        }
        req_obj['hosts'].append(host_obj)


    body = json.dumps(req_obj)
    sig_str = wallet.sign_bitcoin_message(body, pkh)
    if not wallet.verify_bitcoin_message(body, sig_str, pkh):
        print("Cannot self-verify message")
        sys.exit(1)

    sel_url = ctx.obj['endpoint'] + 'dns/1/records.update'
    headers = {
        'Content-Type': 'application/json',
        'X-Bitcoin-Sig': sig_str,
    }
    answer = requests.post(url=sel_url.format(), headers=headers, data=body)
    print(answer.text)

@click.command(name='delete')
@click.argument('name')
@click.argument('domain')
@click.argument('pkh')
@click.pass_context
def cmd_delete(ctx, name, domain, pkh):
    req_obj = {
        'name': name,
        'domain': domain,
        'pkh': pkh
    }

    body = json.dumps(req_obj)
    sig_str = wallet.sign_bitcoin_message(body, pkh)
    if not wallet.verify_bitcoin_message(body, sig_str, pkh):
        print("Cannot self-verify message")
        sys.exit(1)

    sel_url = ctx.obj['endpoint'] + 'dns/1/host.delete'
    headers = {
        'Content-Type': 'application/json',
        'X-Bitcoin-Sig': sig_str,
    }
    answer = requests.post(url=sel_url.format(), headers=headers, data=body)
    print(answer.text)

main.add_command(cmd_info)
main.add_command(cmd_domains)
main.add_command(cmd_register)
main.add_command(cmd_simpleRegister)
main.add_command(cmd_update)
main.add_command(cmd_delete)

if __name__ == "__main__":
    main()

