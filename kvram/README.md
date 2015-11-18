
kvram - Simple key/value API
============================

Summary:  In-memory key/value database.  Simple, unreliable RAM storage API.

Pricing theory:  Each request charges per byte, with a minimum price floor.

Future work / caveats:

* Entries are never stored.  Each server restart empties database.
* Entries are never deleted.
* Potential for running out of memory (while being paid to do so).


First time setup
----------------
None


Running the server
------------------
$ python3 kvram-server.py

The server starts with an empty in-memory database.


API;

1. Get value
------------

HTTP URI: /get

Params:

	key	Binary string, 1-512 bytes

Result if key found:

	Binary string, 0-1000000 bytes

Result if key not found:

	Binary string, 0 bytes

Pricing:

	Byte length of value, in satoshis.  Minimum 1.


2. Store key+value
------------------

HTTP URI: /put

Params:

	key	Binary string, 1-512 bytes
	value	Binary string, 0-1000000 bytes

Result if successfully stored:

	Binary string, "stored"

Otherwise:

	Binary string, containing an error message

Pricing:

	Byte length of key +
	Byte length of value, in satoshis.  Minimum 2.


