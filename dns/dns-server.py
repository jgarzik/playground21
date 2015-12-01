import os
import json
import binascii
import srvdb
import re
import base58
import ipaddress
import pprint

# import flask web microframework
from flask import Flask
from flask import request
from flask import abort

# import from the 21 Developer Library
from two1.lib.bitcoin.txn import Transaction
from two1.lib.bitcoin.crypto import PublicKey
from two1.lib.wallet import Wallet, exceptions
from two1.lib.bitserv.flask import Payment

USCENT=2801

pp = pprint.PrettyPrinter(indent=2)

db = srvdb.SrvDb('dns.db')

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

name_re = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]*$")

def valid_name(name):
    if not name or len(name) < 1 or len(name) > 64:
        return False
    if not name_re.match(name):
        return False
    return True

@app.route('/dns/1/domains')
def get_domains():
    try:
        domains = db.domains()
    except:
        abort(500)

    body = json.dumps(domains, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

def parse_hosts(name, in_obj):
    host_records = []
    try:
        if (not 'hosts' in in_obj):
            return host_records

        hosts = in_obj['hosts']
        for host in hosts:
            rec_type = host['rec_type']
            ttl = int(host['ttl'])

            if ttl < 30 or ttl > (24 * 60 * 60 * 7):
                return "Invalid TTL"

            if rec_type == 'A':
                address = ipaddress.IPv4Address(host['address'])
            elif rec_type == 'AAAA':
                address = ipaddress.IPv6Address(host['address'])
            else:
                return "Invalid rec type"

            host_rec = (name, rec_type, str(address), ttl)
            host_records.append(host_rec)

    except:
        return "JSON validation exception"

    return host_records


def get_price_register(request):
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
        days = int(in_obj['days'])
    except:
        return 0
    if days < 1 or days > 365:
        return 0

    price = int(USCENT / 10) * days

    return price

@app.route('/dns/1/host.register', methods=['POST'])
@payment.required(get_price_register)
def cmd_host_register():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    try:
        if (not 'name' in in_obj):
            return ("Missing name", 400, {'Content-Type':'text/plain'})

        name = in_obj['name']
        pkh = None
        days = 1
        if 'pkh' in in_obj:
            pkh = in_obj['pkh']
        if 'days' in in_obj:
            days = int(in_obj['days'])

        if not valid_name(name) or days < 1 or days > 365:
            return ("Invalid name/days", 400, {'Content-Type':'text/plain'})
        if pkh:
            base58.b58decode_check(pkh)
            if (len(pkh) < 20) or (len(pkh) > 40):
                return ("Invalid pkh", 400, {'Content-Type':'text/plain'})
    except:
        return ("JSON validation exception", 400, {'Content-Type':'text/plain'})

    # Validate and collect host records for updating
    host_records = parse_hosts(name, in_obj)
    if isinstance(host_records, str):
        return (host_records, 400, {'Content-Type':'text/plain'})

    # Add to database.  Rely on db to filter out dups.
    try:
        db.add_host(name, days, pkh)
        if len(host_records) > 0:
            db.update_host(name, host_records)
    except:
        return ("Host addition rejected", 400, {'Content-Type':'text/plain'})

    body = json.dumps(True, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

@app.route('/dns/1/host.update', methods=['POST'])
@payment.required(int(USCENT / 3))
def cmd_host_update():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    # Validate JSON object basics
    try:
        if (not 'name' in in_obj or
            not 'hosts' in in_obj):
            return ("Missing name/hosts", 400, {'Content-Type':'text/plain'})

        name = in_obj['name']
        if not valid_name(name):
            return ("Invalid name", 400, {'Content-Type':'text/plain'})
    except:
        return ("JSON validation exception", 400, {'Content-Type':'text/plain'})

    # Validate and collect host records for updating
    host_records = parse_hosts(name, in_obj)
    if isinstance(host_records, str):
        return (host_records, 400, {'Content-Type':'text/plain'})

    # Verify host exists, and is not expired
    try:
        hostinfo = db.get_host(name)
        if hostinfo is None:
            return ("Unknown name", 404, {'Content-Type':'text/plain'})
    except:
        return ("DB Exception", 500, {'Content-Type':'text/plain'})

    # Check permission to update
    pkh = hostinfo['pkh']
    if pkh is None:
        return ("Record update permission denied", 403, {'Content-Type':'text/plain'})
    sig_str = request.headers.get('X-Bitcoin-Sig')
    try:
        if not sig_str or not wallet.verify_bitcoin_message(body, sig_str, pkh):
            return ("Record update permission denied", 403, {'Content-Type':'text/plain'})
    except:
        return ("Record update permission denied", 403, {'Content-Type':'text/plain'})

    # Add to database.  Rely on db to filter out dups.
    try:
        db.update_host(name, host_records)
    except:
        return ("DB Exception", 400, {'Content-Type':'text/plain'})

    body = json.dumps(True, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

@app.route('/dns/1/host.delete', methods=['POST'])
def cmd_host_delete():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    # Validate JSON object basics
    try:
        if (not 'name' in in_obj or
            not 'pkh' in in_obj):
            return ("Missing name/pkh", 400, {'Content-Type':'text/plain'})

        name = in_obj['name']
        pkh = in_obj['pkh']
        if (not valid_name(name) or (len(pkh) < 10)):
            return ("Invalid name", 400, {'Content-Type':'text/plain'})
    except:
        return ("JSON validation exception", 400, {'Content-Type':'text/plain'})

    # Verify host exists, and is not expired
    try:
        hostinfo = db.get_host(name)
        if hostinfo is None:
            return ("Unknown name", 404, {'Content-Type':'text/plain'})
    except:
        return ("DB Exception - get host", 500, {'Content-Type':'text/plain'})

    # Check permission to update
    if (hostinfo['pkh'] is None) or (pkh != hostinfo['pkh']):
        return ("Record update permission denied", 403, {'Content-Type':'text/plain'})
    sig_str = request.headers.get('X-Bitcoin-Sig')
    try:
        if not sig_str or not wallet.verify_bitcoin_message(body, sig_str, pkh):
            return ("Record update permission denied", 403, {'Content-Type':'text/plain'})
    except:
        return ("Record update permission denied", 403, {'Content-Type':'text/plain'})

    # Remove from database.  Rely on db to filter out dups.
    try:
        db.delete_host(name)
    except:
        return ("DB Exception - delete host", 400, {'Content-Type':'text/plain'})

    body = json.dumps(True, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

@app.route('/')
def get_info():
    # API endpoint metadata - export list of services
    info_obj = {[
        "name": "dns/1",
        "pricing-type": "per-rpc",
        "pricing": {
            {
                "rpc": "domains",
                "per-req": 0,
            },
            {
                "rpc": "host.register",
                "per-day": int(USCENT / 10),
            },
            {
                "rpc": "host.update",
                "per-req": int(USCENT / 3),
            },
            {
                "rpc": "host.delete",
                "per-req": 0,
            },
        }
    ]}

    body = json.dumps(info_obj, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12005)

