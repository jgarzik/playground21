import os
import json
import binascii
import srvdb
import re
import base58
import ipaddress
import subprocess
import time
import pprint
from httputil import httpjson, http400, http404, http500

# import flask web microframework
from flask import Flask
from flask import request
from flask import abort

# import from the 21 Developer Library
from two1.lib.bitcoin.txn import Transaction
from two1.lib.bitcoin.crypto import PublicKey
from two1.lib.wallet import Wallet, exceptions
from two1.lib.bitserv.flask import Payment

server_config = json.load(open("dns-server.conf"))

USCENT=2824
DNS_SERVER1=server_config["DNS_SERVER1"]
NSUPDATE_KEYFILE=server_config["NSUPDATE_KEYFILE"]
NSUPDATE_LOG=server_config["NSUPDATE_LOG"]
nsupdate_logging=server_config["NSUPDATE_LOGGING"]

pp = pprint.PrettyPrinter(indent=2)

db = srvdb.SrvDb(server_config["DB_PATHNAME"])

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

name_re = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]*$")
name_ns_re = re.compile(r"^ns[0-9]+")

def valid_name(name):
    if not name or len(name) < 1 or len(name) > 64:
        return False
    if not name_re.match(name):
        return False
    return True

def reserved_name(name):
    if name_ns_re.match(name):
        return True
    return False

def nsupdate_cmd(name, domain, host_records):
    pathname = "%s.%s." % (name, domain)

    cmd = "server %s\n" % (DNS_SERVER1,)
    cmd += "zone %s.\n" % (domain,)
    cmd += "update delete %s\n" % (pathname,)

    for rec in host_records:
        cmd += "update add %s %d %s %s\n" % (pathname, rec[4], rec[2], rec[3])

    cmd += "show\n"
    cmd += "send\n"

    return cmd.encode('utf-8')

def nsupdate_exec(name, domain, host_records):
    nsupdate_input = nsupdate_cmd(name, domain, host_records)
    args = [
        "/usr/bin/nsupdate",
        "-k", NSUPDATE_KEYFILE,
        "-v",
    ]
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(input=nsupdate_input, timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate(input=nsupdate_input)

    if nsupdate_logging:
        with open(NSUPDATE_LOG, 'a') as f:
            f.write("timestamp %lu\n" % (int(time.time()),))
            f.write(outs.decode('utf-8') + "\n")
            f.write(errs.decode('utf-8') + "\n")
            f.write("---------------------------------------------\n")

    if proc.returncode is None or proc.returncode != 0:
        return False
    return True

@app.route('/dns/1/domains')
def get_domains():
    try:
        domains = db.domains()
    except:
        abort(500)

    return httpjson(domains)

def parse_hosts(name, domain, in_obj):
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

            host_rec = (name, domain, rec_type, str(address), ttl)
            host_records.append(host_rec)

    except:
        return "JSON validation exception"

    return host_records

def store_host(name, domain, days, pkh, host_records):
    # Add to database.  Rely on db to filter out dups.
    try:
        db.add_host(name, domain, days, pkh)
        if len(host_records) > 0:
            if not nsupdate_exec(name, domain, host_records):
                http500("nsupdate failure")
            db.update_records(name, domain, host_records)
    except:
        return http400("Host addition rejected")

    return httpjson(True)

def get_price_register_days(days):
    if days < 1 or days > 365:
        return 0

    price = int(USCENT / 50) * days

    return price

def get_price_register(request):
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
        days = int(in_obj['days'])
    except:
        return 0

    return get_price_register_days(days)

@app.route('/dns/1/host.register', methods=['POST'])
@payment.required(get_price_register)
def cmd_host_register():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return http400("JSON Decode failed")

    try:
        if (not 'name' in in_obj or
            not 'domain' in in_obj):
            return http400("Missing name/domain")

        name = in_obj['name']
        domain = in_obj['domain']
        pkh = None
        days = 1
        if 'pkh' in in_obj:
            pkh = in_obj['pkh']
        if 'days' in in_obj:
            days = int(in_obj['days'])

        if not valid_name(name) or days < 1 or days > 365:
            return http400("Invalid name/days")
        if not db.valid_domain(domain):
            return http404("Domain not found")
        if pkh:
            base58.b58decode_check(pkh)
            if (len(pkh) < 20) or (len(pkh) > 40):
                return http400("Invalid pkh")
    except:
        return http400("JSON validation exception")

    # Check against reserved host name list
    if reserved_name(name):
        return http400("Reserved name.  Name not available for registration.")

    # Validate and collect host records for updating
    host_records = parse_hosts(name, domain, in_obj)
    if isinstance(host_records, str):
        return http400(host_records)

    return store_host(name, domain, days, pkh, host_records)

def get_price_register_simple(request):
    try:
        name = request.args.get('name')
        domain = request.args.get('domain')
        days = int(request.args.get('days'))
        ip = request.args.get('ip')
        address = ipaddress.ip_address(ip)
        if (not valid_name(name) or days < 1 or days > 365 or
            not db.valid_domain(domain)):
            return 0
    except:
        return 0

    return get_price_register_days(days)

@app.route('/dns/1/simpleRegister')
@payment.required(get_price_register_simple)
def cmd_host_simpleRegister():
    try:
        name = request.args.get('name')
        domain = request.args.get('domain')
        days = int(request.args.get('days'))
        ip = request.args.get('ip')

        if not valid_name(name) or days < 1 or days > 365:
            return http400("Invalid name/days")
        if not db.valid_domain(domain):
            return http404("Domain not found")
    except:
        return http400("Invalid name / domain / days supplied")

    try:
        address = ipaddress.ip_address(ip)
    except:
        return http400("Invalid IP address supplied")

    if isinstance(address, ipaddress.IPv4Address):
        rec_type = 'A'
    elif isinstance(address, ipaddress.IPv6Address):
        rec_type = 'AAAA'
    else:
        return http500("bonkers")

    # Check against reserved host name list
    if reserved_name(name):
        return http400("Reserved name.  Name not available for registration.")

    # Validate and collect host records
    host_records = []
    host_rec = (name, domain, rec_type, str(address), 1000)
    host_records.append(host_rec)

    return store_host(name, domain, days, None, host_records)

@app.route('/dns/1/records.update', methods=['POST'])
@payment.required(int(USCENT / 5))
def cmd_host_update():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return http400("JSON Decode failed")

    # Validate JSON object basics
    try:
        if (not 'name' in in_obj or
            not 'domain' in in_obj or
            not 'hosts' in in_obj):
            return http400("Missing name/hosts")

        name = in_obj['name']
        domain = in_obj['domain']
        if not valid_name(name):
            return http400("Invalid name")
        if not db.valid_domain(domain):
            return http404("Domain not found")
    except:
        return http400("JSON validation exception")

    # Validate and collect host records for updating
    host_records = parse_hosts(name, domain, in_obj)
    if isinstance(host_records, str):
        return http400(host_records)

    # Verify host exists, and is not expired
    try:
        hostinfo = db.get_host(name, domain)
        if hostinfo is None:
            return http404("Unknown name")
    except:
        return http500("DB Exception")

    # Check permission to update
    pkh = hostinfo['pkh']
    if pkh is None:
        abort(403)
    sig_str = request.headers.get('X-Bitcoin-Sig')
    try:
        if not sig_str or not wallet.verify_bitcoin_message(body, sig_str, pkh):
            abort(403)
    except:
        abort(403)

    # Add to database.  Rely on db to filter out dups.
    try:
        if not nsupdate_exec(name, domain, host_records):
            http500("nsupdate failure")
        db.update_records(name, domain, host_records)
    except:
        return http400("DB Exception")

    return httpjson(True)

@app.route('/dns/1/host.delete', methods=['POST'])
def cmd_host_delete():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return http400("JSON Decode failed")

    # Validate JSON object basics
    try:
        if (not 'name' in in_obj or
            not 'domain' in in_obj or
            not 'pkh' in in_obj):
            return http400("Missing name/pkh")

        name = in_obj['name']
        domain = in_obj['domain']
        pkh = in_obj['pkh']
        if (not valid_name(name) or (len(pkh) < 10)):
            return http400("Invalid name")
        if not db.valid_domain(domain):
            return http404("Domain not found")
    except:
        return http400("JSON validation exception")

    # Verify host exists, and is not expired
    try:
        hostinfo = db.get_host(name, domain)
        if hostinfo is None:
            return http404("Unknown name")
    except:
        return http500("DB Exception - get host")

    # Check permission to update
    if (hostinfo['pkh'] is None) or (pkh != hostinfo['pkh']):
        abort(403)
    sig_str = request.headers.get('X-Bitcoin-Sig')
    try:
        if not sig_str or not wallet.verify_bitcoin_message(body, sig_str, pkh):
            abort(403)
    except:
        abort(403)

    # Remove from database.  Rely on db to filter out dups.
    try:
        if not nsupdate_exec(name, domain, []):
            http500("nsupdate failure")
        db.delete_host(name, domain)
    except:
        return http400("DB Exception - delete host")

    return httpjson(True)

@app.route('/')
def get_info():
    # API endpoint metadata - export list of services
    info_obj = [{
        "name": "dns/1",
        "website": "https://github.com/jgarzik/playground21/tree/master/dns",
        "pricing-type": "per-rpc",
        "pricing": [
            {
                "rpc": "domains",
                "per-req": 0,
            },
            {
                "rpc": "host.register",
                "per-day": int(USCENT / 50),
            },
            {
                "rpc": "simpleRegister",
                "per-day": int(USCENT / 50),
            },
            {
                "rpc": "records.update",
                "per-req": int(USCENT / 5),
            },
            {
                "rpc": "host.delete",
                "per-req": 0,
            },
        ]
    }]
    return httpjson(info_obj)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12005)

