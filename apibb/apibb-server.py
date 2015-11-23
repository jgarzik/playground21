import os
import re
import json
import random
import apsw
import time

# import flask web microframework
from flask import Flask
from flask import request

# import from the 21 Developer Library
from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment

connection = apsw.Connection("apibb.db")

name_re = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-\.]*$")

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

def expire_ads():
    cursor = connection.cursor()
    cursor.execute("DELETE FROM ads WHERE expires < datetime('now')")

def expire_names():
    cursor = connection.cursor()
    cursor.execute("DELETE FROM names WHERE expires < datetime('now')")

@app.route('/names')
@payment.required(1)
def get_names():
    cursor = connection.cursor()
    rv = []
    for name,created,expires in cursor.execute("SELECT name,created,expires FROM names ORDER BY name"):
        obj = {
            "name": name,
            "created": created,
            "expires": expires
        }
        rv.append(obj)

    return json.dumps(rv)

def valid_renewal(request):
    name = request.args.get('name')
    hours = request.args.get('hours')

    if (name_re.match(name) is None or
        int(hours) < 1 or
        int(hours) > (24 * 30)):
        return False

    return True

def get_renew_price_from_req(request):
    if not valid_renewal(request):
        return "invalid advertisement"

    hours = int(request.args.get('hours'))

    price = hours * 10		# 10 satoshis per hour

    if price < 10:
        price = 10
    return price

@app.route('/namerenew')
@payment.required(get_renew_price_from_req)
def name_renew():
    if not valid_renewal(request):
        return "invalid renewal"

    expire_names()

    name = request.args.get('name')
    hours = int(request.args.get('hours'))

    cursor = connection.cursor()
    expires = 0
    for v in cursor.execute("SELECT expires FROM names WHERE name = ?", (name,)):
        expires = v[0]

    print("EXPIRES " + str(expires))

    if expires == 0:
        cursor.execute("INSERT INTO names VALUES(?, datetime('now'), datetime('now', '+" + str(hours) + " hours'))", (name,))
    else:
        cursor.execute("UPDATE names SET expires = datetime(?, '+" + str(hours) + " hours') WHERE name = ?", (expires, name))

    return "OK"

def valid_advertisement(cursor, request):
    name = request.args.get('name')
    uri = request.args.get('uri')
    pubkey = request.args.get('pubkey')
    hours = request.args.get('hours')

    if (name_re.match(name) is None or
        len(uri) < 1 or
        len(uri) > 512 or
        len(pubkey) < 32 or
        len(pubkey) > 512 or
        int(hours) < 1 or
        int(hours) > (24 * 30)):
        return False

    expires = None
    for v in cursor.execute("SELECT strftime('%s', expires) FROM names WHERE name = ? AND expires > datetime('now')", (name,)):
        expires = v

    if expires is None:
        return False

#    curtime = int(time.time())
#    curtime_deltap = curtime + (int(hours) * 60 * 60)
#    if curtime_deltap > expires:
#        return False

    return True

def get_advertise_price_from_req(request):
    cursor = connection.cursor()
    if not valid_advertisement(cursor, request):
        return "invalid advertisement"

    hours = int(request.args.get('hours'))

    price = hours * 2		# 2 satoshis per hour

    if price < 2:
        price = 2
    return price

@app.route('/advertise')
@payment.required(get_advertise_price_from_req)
def advertise():
    cursor = connection.cursor()
    if not valid_advertisement(cursor, request):
        return "invalid advertisement"

    name = request.args.get('name')
    uri = request.args.get('uri')
    pubkey = request.args.get('pubkey')
    hours = request.args.get('hours')

    cursor.execute("INSERT INTO ads VALUES(?, ?, ?, datetime('now'), datetime('now','+" + str(hours) + " hours'))", (name, uri, pubkey))

    return "OK"

@app.route('/ads')
@payment.required(1)
def get_advertisements():
    name = request.args.get('name')

    rv = []
    cursor = connection.cursor()
    for uri,pk,created,expires in cursor.execute("SELECT uri,pubkey,created,expires FROM ads WHERE name = ? AND expires > datetime('now')", (name,)):
        obj = {
            "uri": uri,
            "pubkey": pk,
            "created": created,
            "expires": expires
        }
        rv.append(obj)

    return json.dumps(rv)

@app.route('/')
def get_info():
    info_obj = {
        "name": "apibb",
        "version": 100,
        "pricing": {
            "/names" : {
                "minimum" : 1
            },
            "/namerenew" : {
                "minimum" : 10
            },
            "/advertise" : {
                "minimum" : 2
            },
            "/ads" : {
                "minimum" : 1
            },
        }

    }
    body = json.dumps(info_obj, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12002)

