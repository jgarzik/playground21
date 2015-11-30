import os
import json
import binascii
import hashlib
import srvdb
import re
import base58
import ipaddress
import pprint
import time

import worktmp
import util

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

db = srvdb.SrvDb('turk.db')

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

@app.route('/task/<id>')
@payment.required(int(USCENT / 100))
def get_task(id):
    try:
        pkh_str = request.headers.get('X-Bitcoin-PKH')
        sig_str = request.headers.get('X-Bitcoin-Sig')

        tstamp = int(request.headers.get('X-Timestamp'))
        curtime = int(time.time())
        min_time = min(tstamp, curtime)
        max_time = max(tstamp, curtime)
        time_diff = max_time - min_time
        if (time_diff > 15):
            return ("Clock drift", 403, {'Content-Type':'text/plain'})

        msg = util.hash_task_phdr(id, pkh_str, tstamp)
        if not wallet.verify_bitcoin_message(msg, sig_str, pkh_str):
            return ("Permission denied", 403, {'Content-Type':'text/plain'})
    except:
        return ("Permission denied", 403, {'Content-Type':'text/plain'})

    try:
        worker = db.worker_get(pkh_str)
        if worker is None:
            return ("Permission denied", 403, {'Content-Type':'text/plain'})

        task = db.task_get(id)
        if task is None:
            abort(404)
    except:
        abort(500)

    body = json.dumps(task, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

@app.route('/tasks.list')
@payment.required(10)
def get_tasks():
    try:
        tasks = db.tasks()
    except:
        abort(500)

    body = json.dumps(tasks, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

@app.route('/task.new', methods=['POST'])
@payment.required(USCENT * 10)
def cmd_task_new():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    # Validate JSON object basics
    try:
        if (not 'pkh' in in_obj or
            not 'summary' in in_obj or
            not 'image' in in_obj or
            not 'image_ctype' in in_obj or
            not 'template' in in_obj or
            not 'min_workers' in in_obj or
            not 'reward' in in_obj):
            return ("Missing params", 400, {'Content-Type':'text/plain'})

        pkh = in_obj['pkh']
        summary = in_obj['summary']
        image = binascii.unhexlify(in_obj['image'])
        image_ctype = in_obj['image_ctype']
        template = in_obj['template']
        min_workers = int(in_obj['min_workers'])
        reward = int(in_obj['reward'])

        base58.b58decode_check(pkh)
    except:
        return ("JSON validation exception", 400, {'Content-Type':'text/plain'})

    # Check work template
    wt = worktmp.WorkTemplate()
    wt.set(template)
    if not wt.valid():
        return ("JSON template validation failed", 400, {'Content-Type':'text/plain'})

    # Generate unique id
    time_str = str(int(time.time()))
    md = hashlib.sha256()
    md.update(time_str.encode('utf-8'))
    md.update(body.encode('utf-8'))
    id = md.hexdigest()

    # Add worker to database.  Rely on db to filter out dups.
    try:
        template_json = json.dumps(template)
        db.task_add(id, summary, pkh, image, image_ctype, template_json, min_workers, reward)
    except:
        return ("DB Exception - add task", 400, {'Content-Type':'text/plain'})

    return (id, 200, {
        'Content-length': len(body),
        'Content-type': 'text/plain',
    })

@app.route('/worker.new', methods=['POST'])
@payment.required(USCENT * 10)
def cmd_worker_new():

    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    # Validate JSON object basics
    try:
        if (not 'payout_addr' in in_obj or
            not 'pkh' in in_obj):
            return ("Missing name/pkh", 400, {'Content-Type':'text/plain'})

        pkh = in_obj['pkh']
        payout_addr = in_obj['payout_addr']

        base58.b58decode_check(pkh)
        base58.b58decode_check(payout_addr)
    except:
        return ("JSON validation exception", 400, {'Content-Type':'text/plain'})

    # Add worker to database.  Rely on db to filter out dups.
    try:
        db.worker_add(pkh, payout_addr)
    except:
        return ("DB Exception - add worker", 400, {'Content-Type':'text/plain'})

    body = json.dumps(True, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

@app.route('/')
def get_info():
    info_obj = {
        "name": "turk",
        "version": 100,
        "pricing": {
            "/worker.new" : {
               "minimum" : (USCENT * 10)
            },
            "/task.new" : {
               "minimum" : (USCENT * 10)
            },
            "/task/" : {
               "minimum" : int(USCENT / 100)
            },
            "/tasks.list" : {
               "minimum" : 10
            },
        }

    }
    body = json.dumps(info_obj, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12007, debug=True)

