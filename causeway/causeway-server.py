#!/usr/bin/env python3

import os, json, random, time, string
from settings import *

from flask import Flask
from flask import request
from flask import send_from_directory
from flask import abort, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)
wallet = Wallet()
payment = Payment(app, wallet)

# start time
start_time = time.time()
stored = 0

# get a list of the files in the directory
file_list = os.listdir(DATA_DIR)

# simple content model: dictionary of files w/ random prices
files = {}
for file_id in range(len(file_list)):
    file_name = file_list[file_id]
    size = os.path.getsize(os.path.join(DATA_DIR, file_name))
    price = size / 1024 / 50 * PRICE
    if price < 1000:
        price = 1000
    files[file_id+1] = file_name, size, price

"""
@app.route('/buy', methods=['POST'])
@payment.required(get_price_from_request)
def buy_storage():
    '''Stores selected file if payment is made.'''
    # extract data from client request
    key = request.get_json.get('key', '')
    value = request.get_json.get('value', '')
    address = request.get_json.get('address', '')
    nonce = request.get_json.get('nonce', '')
    signature = request.get_json().get('signature', '')

    # check if selection is valid
    if(sel < 1 or sel > len(file_list)):
         return abort(500)
    else:
"""

@app.route('/status')
def status():
    '''Return general info about server instance. '''
    uptime = str(int(time.time() - start_time))
    st = os.statvfs(DATA_DIR)
    free = st.f_bavail * st.f_frsize
    return json.dumps({'uptime': uptime,
                       'stored': str(stored),
                       'free': str(free),
                       'price': str(PRICE)
                       }, indent=4
                      )

@app.route('/price')
def price():
    '''Return price for 1MB storage with bundled 50MB transfer.'''
    return json.dumps({'price': PRICE}, indent=4)

@app.route('/nonce')
def nonce():
    '''Return 32-byte nonce for generating non-reusable signatures..'''
    from models import Owner
    # check if user exists
    o = Owner.query.get(request.args.get('address'))
    if o is None:
        return abort(500)

    # check if nonce is set for user
    if len(o.nonce) == 32:
        return json.dumps({'nonce': nonce}, indent=4)
    # if not, create one and store it
    else:
        n = ''.join(random.SystemRandom().choice(string.hexdigits) for _ in range(32))
        o.nonce = n.lower()
        db.session.commit()
        return json.dumps({'nonce': o.nonce}, indent=4)

@app.route('/files')
def file_lookup():
    '''List available files, size, and price.'''
    return json.dumps(files)


def get_price_from_request(request):
    '''Return the price of the selected file.'''
    id = int(request.args.get('selection'))
    return files[id][1]

"""
@app.route('/buy')
@payment.required(get_price_from_request)
def buy_file():
    '''Returns selected file if payment is made.'''
    # extract selection from client request
    sel = int(request.args.get('selection'))

    # check if selection is valid
    if(sel < 1 or sel > len(file_list)):
         return abort(500)
    else:
        return send_from_directory(DATA_DIR, file_list[int(sel)-1])
"""

def has_no_empty_params(rule):
    '''Testing rules to identify routes.'''
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/help')
def help():
    '''Returns list of defined routes.'''
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)

    return json.dumps(links, indent=4)

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=SERVER_PORT)
