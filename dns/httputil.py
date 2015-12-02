
import json

def httpjson(val):
    body = json.dumps(val, indent=2)
    return (body, 200, {
        'Content-length': len(body),
        'Content-type': 'application/json',
    })

def http400(msg):
    if not msg:
        msg = "Invalid request"
    return (msg, 400, {'Content-Type':'text/plain'})

def http404(msg):
    if not msg:
        msg = "Not found"
    return (msg, 404, {'Content-Type':'text/plain'})

def http500(msg):
    if not msg:
        msg = "Internal server error"
    return (msg, 500, {'Content-Type':'text/plain'})

