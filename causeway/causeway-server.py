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

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)
wallet = Wallet()
payment = Payment(app, wallet)

# start time
start_time = time.time()
stored = 0

@app.route('/')
@app.route('/help')
def home():
    '''Return service, pricing and endpoint information'''
    home_obj = [{"name": "causeway/1",       # service 'causeway', version '1'
                 "pricing-type": "per-mb",   # pricing is listed per 1000000 bytes
                 "pricing" : [{"rpc": "buy",
                               "per-req": 0,
                               "per-unit": PRICE,
                               "description": "1 MB hosting, 50 MB bandwidth, 1 year expiration"
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
                              }],
                  "description": "This Causeway server provides microhosting services. Download the "\
                  "client and server at https://github.com/jgarzik/playground21/archive/master.zip"
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
    '''Registers one hosting bucket to account on paid request.'''
    # extract account address from client request
    owner = request.args.get('address')
    contact = request.args.get('contact')

    # check if user exists
    o = db.session.query(Owner).get(owner)
    if o is None:
        # create them
        o = Owner(owner)
        db.session.add(o)
        db.session.commit()

    # owner should now exist,  create sale record for address
    s = Sale(owner, contact, 1, 30, PRICE)
    db.session.add(s)
    db.session.commit()

    body = json.dumps({'result': 'success', 
                       'buckets': s.get_buckets()}, indent=2)
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/put', methods=['POST'])
def put():
    '''Store a key-value pair.'''
    # get size of file sent
    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    k = in_obj['key']
    v = in_obj['value']
    o = in_obj['address']
    n = in_obj['nonce']
    s = in_obj['signature']
     
    # check signature
    owner = Owner.query.filter_by(address=o).first()
    if owner.nonce not in n or wallet.verify_bitcoin_message(k + v + o + n, s, o):
        body = json.dumps({'error': 'Incorrect signature.'})
        code = 401
    else:
        size = len(k) + len(v)

        # check if owner has enough free storage
        # get free space from each of owner's buckets
        result = db.engine.execute('select * from sale where julianday("now") - \
                    julianday(sale.created) < sale.term order by sale.created desc')
        # choose newest bucket that has enough space
        sale_id = None
        for row in result:
            if (row[7] + size) < (1024 * 1024):
                sale_id = row[0]
    
        if sale_id is None:     # we couldn't find enough free space
            body = json.dumps({'error': 'Insufficient storage space.'})
            code = 403 
        else:
            # check if key already exists and is owned by the same owner
            kv = db.session.query(Kv).filter_by(key=k).filter_by(owner=o).first()
                    
            if kv is None:
                kv = Kv(k, v, o, sale_id)
                db.session.add(kv)
                db.session.commit()
            else:
                kv.value = v
                db.session.commit()
    
            s = db.session.query(Sale).get(sale_id)
            s.bytes_used = s.bytes_used + size
            db.session.commit()
            body = json.dumps({'result': 'success'})
            code = 201
    
    return (body, code, {'Content-length': len(body),
                        'Content-type': 'application/json',
                        }
           )

@app.route('/delete', methods=['POST'])
def delete():
    '''Delete a key-value pair.'''
    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    k = in_obj['key']
    o = in_obj['address']
    n = in_obj['nonce']
    s = in_obj['signature']

    # check signature
    owner = Owner.query.filter_by(address=o).first()
    if owner.nonce not in n or wallet.verify_bitcoin_message(k + o + n, s, o):
        body = json.dumps({'error': 'Incorrect signature.'})
        code = 401
    else:
        # check if key already exists and is owned by the same owner
        kv = db.session.query(Kv).filter_by(key=k).filter_by(owner=o).first()
        if kv is None:
            body = json.dumps({'error': 'Key not found or not owned by caller.'})
            code = 404
        else:
            # free up storage quota and remove kv
            size = len(kv.value)
            sale_id = kv.sale
            s = db.session.query(Sale).get(sale_id)
            s.bytes_used = s.bytes_used - size
            db.session.delete(kv)
            db.session.commit()
            body = json.dumps({'result': 'success'})
            code = 200
    
    return (body, code, {'Content-length': len(body),
                         'Content-type': 'application/json',
                        }
           )

@app.route('/get')
def get():
    '''Get a key-value pair.'''
    
    key = request.args.get('key')

    kv = Kv.query.filter_by(key=key).first()

    if kv is None:
        body = json.dumps({'error': 'Key not found.'})
        code = 404
    else:
        body = json.dumps({'key': key, 'value': kv.value})
        code = 200

    # calculate size and check against quota on kv's sale record
    return (body, code, {'Content-length': len(body),
                        'Content-type': 'application/json',
                        }
           )

@app.route('/nonce')
def nonce():
    '''Return 32-byte nonce for generating non-reusable signatures..'''
    # check if user exists
    o = db.session.query(Owner).get(request.args.get('address'))
    if o is None:
        return abort(500)

    # if nonce is set for user return it, else make a new one
    if o.nonce and len(o.nonce) == 32:
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
