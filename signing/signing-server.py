import os
import apsw
import json
import binascii

# import flask web microframework
from flask import Flask
from flask import request
from flask import abort

# import from the 21 Developer Library
from two1.lib.bitcoin.txn import Transaction
from two1.lib.bitcoin.crypto import PublicKey
from two1.lib.wallet import Wallet, exceptions
from two1.lib.bitserv.flask import Payment

connection = apsw.Connection("signing.db")

SRV_ACCT = 'signing'

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

# Create wallet account for these contracts
try:
    wallet.create_account(SRV_ACCT)
except exceptions.AccountCreationError:
    pass

def srvdb_last_idx(cursor):
    row = cursor.execute("SELECT MAX(hd_index) FROM metadata").fetchone()
    if row is None:
        return 0
    return int(row[0])

@app.route('/new')
@payment.required(1000)
def cmd_new():
    # Get hex-encoded input (owner) public key
    try:
        owner_pubkey = PublicKey.from_bytes(request.args.get('owner'))
    except:
        abort(400)

    # Generate next available HD wallet index
    try:
        cursor = connection.cursor()
        next_idx = srvdb_last_idx(cursor) + 1
    except:
        abort(500)

    # Derive HD public key
    acct = wallet._check_and_get_accounts([SRV_ACCT])
    hd_pubkey = acct.get_public_key(False, next_idx)
    pubkey = binascii.hexlify(hd_public.compressed_bytes())
    address = hd_pubkey.address()
    owner_b64 = owner_pubkey.to_base64()

    # Add public key to db
    try:
        cursor.execute("INSERT INTO metadata VALUES(?, ?, ?, ?)", (address, pubkey, next_idx, owner_b64))
    except:
        abort(500)

    # Return contract id, public key
    obj = {
        'id': next_idx,
        'contract_key': pubkey,
    }

    body = json.dumps(ret_obj, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })


@app.route('/sign/<int:id>', methods=['PUT'])
@payment.required(1000)
def cmd_sign(id):
    body = request.data
    body_len = len(body)

    # get associated metadata
    try:
        cursor = connection.cursor()
        row = cursor.execute("SELECT * FROM metadata WHERE hd_index = ?", (id,)).fetchone()
        if row is None:
            abort(404)

        hd_index = int(row[0])
        owner_key = PublicKey.from_bytes(row[3])
    except:
        abort(500)

    # check content-length
    clen_str = request.headers.get('content-length')
    if clen_str is None:
        abort(400)
    clen = int(clen_str)
    if clen != body_len:
        abort(400)

    # check content-type
    ctype = request.headers.get('content-type')
    if ctype is None or ctype != 'application/json':
        abort(400)

    # parse JSON body
    try:
        in_obj = json.loads(body)
        if (not 'msg' in in_obj or not 'sig' in in_obj or
            not 'hash_type' in in_obj or
            not 'input_idx' in in_obj or not 'script' in in_obj):
            abort(400)
        hash_type = int(in_obj['hash_type'])
        input_idx = int(in_obj['input_idx'])
        script = Script.from_bytes(binascii.unhexlify(in_obj['script']))
        tx_hex = binascii.unhexlify(in_obj['msg'])

        broadcast = False
        if 'broadcast' in in_obj and in_obj['broadcast'] == True:
            broadcast = True
    except:
        abort(400)

    # validate base64-encoded signature on hex-encoded transaction
    try:
        rc = PublicKey.verify_bitcoin(tx_hex, in_obj['sig'], owner_key.address())
        if not rc:
            abort(400)

        tx = Transaction.from_hex(tx_hex)
    except:
        abort(400)
        
    # get HD wallet account, privkey for this contract
    acct = wallet._check_and_get_accounts([SRV_ACCT])
    hd_privkey = acct.get_private_key(False, hd_index)

    # try to sign the input
    try:
        tx.sign_input(input_idx, hash_type, hd_privkey, script)
    except:
        abort(400)

    # broadcast transaction to network
    if broadcast:
        wallet.broadcast(tx)

    # return updated transaction
    output_data = tx.to_hex()

    return (output_data, 200, {
        'Content-length': len(output_data),
        'Content-type': 'text/plain',
    })


@app.route('/')
def get_info():
    info_obj = {
        "name": "signing",
        "version": 100,
        "pricing": {
            "/new" : {
                "minimum" : 1000
            },
            "/sign" : {
                "minimum" : 1000
            },
        }

    }
    body = json.dumps(info_obj, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12004)

