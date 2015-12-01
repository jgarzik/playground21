import os
import json
import random
import subprocess
import tempfile

# import flask web microframework
from flask import Flask
from flask import request
from flask import abort
from werkzeug import secure_filename

# import from the 21 Developer Library
from two1.lib.wallet import Wallet
from two1.lib.bitserv.flask import Payment

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

@app.route('/encode', methods=['POST'])
@payment.required(10)
def encode():
    clen_str = request.headers.get('content-length')
    if (not clen_str or int(clen_str) > 16000000):
        abort(400)

    file = request.files['file']
    msg_file = request.files['message']
    if not file or not msg_file:
        abort(400)

    filename = secure_filename(file.filename)
    msg_filename = secure_filename(msg_file.filename)
    file.save(filename)
    msg_file.save(msg_filename)

    ctype = file.content_type
    if not ctype:
        ctype = 'application/octet-stream'

    tmp_out = tempfile.NamedTemporaryFile(suffix=".txt")

    proc = subprocess.Popen(["/usr/bin/outguess", "-d", msg_filename, filename, tmp_out.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=10)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    os.remove(filename)
    os.remove(msg_filename)

    if errs:
        body = outs.decode('utf-8') + "\n" + errs.decode('utf-8')
        return (body, 200, {
            'Content-length': len(body),
            'Content-type': 'text/plain',
        })
#        abort(500)

    body = tmp_out.read()
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': ctype,
    })

@app.route('/decode', methods=['POST'])
@payment.required(10)
def decode():
    ctype = request.headers.get('content-type')
    if not ctype:
        ctype = 'application/octet-stream'

    clen_str = request.headers.get('content-length')
    if (not clen_str or int(clen_str) > 16000000):
        abort(400)

    file = request.files['file']
    if not file:
        abort(400)

    in_filename, in_ext = os.path.splitext(file.filename)
    if not in_ext:
        in_ext = ".jpg"

    tmp_in = tempfile.NamedTemporaryFile(suffix=in_ext)
    tmp_in.write(file.read())

    tmp_out = tempfile.NamedTemporaryFile(suffix=".txt")

    proc = subprocess.Popen(["/usr/bin/outguess", "-r", tmp_in.name, tmp_out.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=10)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    if errs:
        body = outs.decode('utf-8') + "\n" + errs.decode('utf-8')
        return (body, 200, {
            'Content-length': len(body),
            'Content-type': 'text/plain',
        })
#        abort(500)

    body = tmp_out.read()
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': ctype,
    })


@app.route('/')
def get_info():
    info_obj = {
        "name": "stegano",
        "version": 100,
        "pricing": {
            "/encode" : {
                "minimum" : 10
            },
            "/decode" : {
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
    app.run(host='0.0.0.0', port=12018, debug=True)

