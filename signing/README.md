
signing - Bitcoin transaction signing server
============================================

WARNING:  Work-in-progress.  Status: untested + feature complete.

Summary:  Create account at signing server.  Sign a bitcoin transaction.

Demonstrates:

* Participating in a P2SH, P2PKH, and/or multisig contract, by generating and providing a public key upon request.

* Signing a bitcoin transaction

* Broadcasting a bitcoin transaction to the bitcoin network

* Public key authentication (only signs transaction for contract based on public key supplied at first contact)


Running the server
------------------

	$ python3 signing-server.py



API;

1. New contract
---------------

HTTP URI: GET /new

Params:

	owner: Hex-encoded ECDSA public key

Result:

	application/json document with the following keys:
	id: contract id (number)
	contract_key: public key associated with this contract, which the signing server will use for signing future bitcoin transactions


Pricing:

	1000 satoshis



2. Sign contract
----------------
HTTP URI: PUT /sign/[contract id]

Params:

	In HTTP body, a application/json document containing the following keys:

	msg: signed message, wrapping a hex-encoded bitcoin transaction
	sig: base64-encoded signature
	input_index: index inside BTC tx to sign
	hash_type: hash type of signature to apply
	script: hex-encoded scriptPubKey / redeem script
	broadcast: if true, broadcast signed TX to network

Result:

	text/plain document containing signed, hex-encoded transaction

Pricing:

	1000 satoshis



