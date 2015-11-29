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
        task = db.task_get(id)
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
            not 'questions' in in_obj or
            not 'min_workers' in in_obj or
            not 'reward' in in_obj):
            return ("Missing params", 400, {'Content-Type':'text/plain'})

        pkh = in_obj['pkh']
        summary = in_obj['summary']
        image = binascii.unhexlify(in_obj['image'])
        image_ctype = in_obj['image_ctype']
        questions = in_obj['questions']
        min_workers = int(in_obj['min_workers'])
        reward = int(in_obj['reward'])

        base58.b58decode_check(pkh)
    except:
        return ("JSON validation exception", 400, {'Content-Type':'text/plain'})

    # Generate unique id
    time_str = str(int(time.time()))
    md = hashlib.sha256()
    md.update(time_str.encode('utf-8'))
    md.update(body.encode('utf-8'))
    id = md.hexdigest()

    # Add worker to database.  Rely on db to filter out dups.
    try:
        questions_json = json.dumps(questions)
        db.task_add(id, summary, pkh, image, image_ctype, questions_json, min_workers, reward)
    except:
        return ("DB Exception - add task", 400, {'Content-Type':'text/plain'})

    body = json.dumps(True, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
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

