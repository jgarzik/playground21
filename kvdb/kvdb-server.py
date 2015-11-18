import os
import json
import random
import apsw

# import flask web microframework
from flask import Flask
from flask import request

# import from the 21 Developer Library
from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment

connection = apsw.Connection("keyvalue.db")

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

def sqldb_query(key):
    cursor = connection.cursor()
    for v in cursor.execute("SELECT v FROM tab WHERE k = ?", (key,)):
        return v
    return ''

def sqldb_store(key, value):
    cursor = connection.cursor()
    cursor.execute("REPLACE INTO tab(k, v) VALUES(?, ?)", (key, value))

def get_get_price_from_request(request):
    key = request.args.get('key')
    price = len(sqldb_query(key))
    if price < 1:
        price = 1
    return price

# endpoint to get a value from the server
@app.route('/get')
@payment.required(get_get_price_from_request)
def load_value():
    key = request.args.get('key')
    cursor = connection.cursor()
    return sqldb_query(key)

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

    sqldb_store(key, value)

    return "stored"

@app.route('/info')
def get_info():
    info_obj = {
	"name": "kvdb",
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
    return json.dumps(info_obj)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12002, debug=True)

