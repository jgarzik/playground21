import os
import json
import random

# import flask web microframework
from flask import Flask
from flask import request

# import from the 21 Developer Library
from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

db = {}

def get_get_price_from_request(request):
    key = request.args.get('key')
    price = 0
    if key in db:
        price = len(db[key])
    if price < 1
        price = 1
    return price

# endpoint to get a value from the server
@app.route('/get')
@payment.required(get_get_price_from_request)
def load_value():
    key = request.args.get('key')
    if key in db:
        return db[key]
    else:
        return ''

def get_put_price_from_request(request):
    key = request.args.get('key')
    value = request.args.get('value')
    total = len(key) + len(value)
    if total < 2:
        total = 2
    return total

@app.route('/put')
@payment.required(get_put_price_from_request)
def store_value():
    key = request.args.get('key')
    value = request.args.get('value')

    if len(key) < 1 or len(key) > 512:
        return "invalid key size"
    if len(value) > 1000000:
        return "value too large"

    db[key] = value

    return "stored"

@app.route('/')
def get_info():
    info_obj = {
	"name": "kvram",
	"version": 100,
        "pricing": {
            "/get" : {
                "minimum" : 1
            },
            "/put" : {
                "minimum" : 2
            }
        }

    }
    return json.dumps(info_obj, indent=2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12001, debug=True)

