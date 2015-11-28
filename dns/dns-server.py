import os
import json
import binascii
import srvdb

# import flask web microframework
from flask import Flask
from flask import request
from flask import abort

# import from the 21 Developer Library
from two1.lib.bitcoin.txn import Transaction
from two1.lib.bitcoin.crypto import PublicKey
from two1.lib.wallet import Wallet, exceptions
from two1.lib.bitserv.flask import Payment

db = srvdb.SrvDb('dns.db')

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

@app.route('/domains')
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

@app.route('/')
def get_info():
    info_obj = {
        "name": "dns",
        "version": 100,
        "pricing": {
            "/domains" : {
                "minimum" : 0
            },
        }

    }
    body = json.dumps(info_obj, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12005, debug=True)

