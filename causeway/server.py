#!/usr/bin/env python3
'''
Causeway Server - key/value storage server geared toward small files with ECSDA signature auth

Usage:
    python3 server.py
'''


import os, json, random, time, string
from settings import DATABASE, PRICE, DATA_DIR, SERVER_PORT

from flask import Flask
from flask import request
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

@app.route('/')
def home():
    '''Return service, pricing and endpoint information'''
    home_obj = [{"name": "causeway/1",       # service 'causeway', version '1'
                 "pricing-type": "per-mb",   # pricing is listed per 1000000 bytes
                 "pricing" : [{"rpc": "buy_storage",
                               "per-req": 0,
                               "per-mb": PRICE
                              },
                              {"rpc": "get",
                               "per-req": 0,
                               "per-mb": 0
                              },
                              {"rpc": "put",
                               "per-req": 0,
                               "per-mb": 0
                              },

                              # default
                              {"rpc": True,        # True indicates default
                               "per-req": 0,
                               "per-mb": 0
                              }]
                }
               ]

    body = json.dumps(home_obj, indent=2)

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/status')
def status():
    '''Return general info about server instance. '''
    uptime = str(int(time.time() - start_time))
    st = os.statvfs(DATA_DIR)
    free = st.f_bavail * st.f_frsize
    body = json.dumps({'uptime': uptime,
                       'stored': str(stored),
                       'free': str(free),
                       'price': str(PRICE)
                      }, indent=2
                     )
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/price')
def price():
    '''Return price for 1MB storage with bundled 50MB transfer.'''
    body = json.dumps({'price': PRICE})
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/buy')
@payment.required(PRICE)
def buy_hosting():
    '''Returns selected file if payment is made.'''
    # extract account address from client request
    owner = request.args.get('address')

    # check if user exists
    o = db.session.query(Owner).get(owner)
    if o is None:
        return abort(500)
    else:
        # create sale record for address
        s = Sale(owner, 1, 30, PRICE)
        s.insert()

    body = json.dumps({'Purchase complete.'}, indent=2)
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/put', methods=['POST'])
def put():
    '''Store a key-value pair.'''
    # get size of file sent
    # check if owner has enough free storage
    # store file in db
    return

@app.route('/get')
def get():
    '''Get a key-value pair.'''
    # calculate size and check against quota on kv's sale record
    return

@app.route('/delete')
def delete():
    '''Delete a key-value pair.'''
    # check if signed by owner
    # delete file
    return

@app.route('/nonce')
def nonce():
    '''Return 32-byte nonce for generating non-reusable signatures..'''
    from models import Owner

    # check if user exists
    o = db.session.query(Owner).get(request.args.get('address'))
    if o is None:
        return abort(500)

    # if nonce is set for user return it, else make a new one
    if len(o.nonce) == 32:
        body = json.dumps({'nonce': o.nonce})
    # if not, create one and store it
    else:
        print("storing")
        n = ''.join(random.SystemRandom().choice(string.hexdigits) for _ in range(32))
        o.nonce = n.lower()
        db.session.commit()
        body = json.dumps({'nonce': o.nonce})

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/address')
def get_deposit_address():
    '''Return new or unused deposit address for on-chain funding.'''
    from models import Owner

    # check if user exists
    o = db.session.query(Owner).get(request.args.get('address'))
    if o is None:
        return abort(500)

    address = request.args.get('address')
    message = request.args.get('contact') + "," + address
    signature = request.args.get('signature')

    print(len(signature))
    if len(signature) == 88 and wallet.verify_bitcoin_message(message, signature, address):
        body = json.dumps({'address': 'hereyago'})
    else:
        body = json.dumps({'error': 'Invalid signature'})

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

def has_no_empty_params(rule):
    '''Testing rules to identify routes.'''
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/info')
def info():
    '''Returns list of defined routes.'''
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)

    return json.dumps(links, indent=2)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=SERVER_PORT)
