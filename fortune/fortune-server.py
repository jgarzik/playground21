import os
import json
import random
import subprocess

# import flask web microframework
from flask import Flask
from flask import request
from flask import abort

# import from the 21 Developer Library
from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

def get_fortune_text():
    proc = subprocess.Popen(["/usr/games/fortune"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=10)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    if errs:
        return None

    return outs

# endpoint to get a value from the server
@app.route('/fortune')
@payment.required(10)
def get_fortune():
    fortune = get_fortune_text()
    if fortune is None:
        abort(500)

    return fortune

@app.route('/')
def get_info():
    info_obj = {
	"name": "fortune",
	"version": 100,
        "pricing": {
            "/fortune" : {
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
    app.run(host='0.0.0.0', port=12012)

