
dns - Dynamic DNS management service (working skeleton)
=======================================================

Summary:  DNS management service, suitable for proxying to e.g. Namecheap

Demonstrates:

* Flask error handling, file upload.

* Public key authentication - Remote client provides public key from 21BC
  wallet, to enable permissioned record updates.

* Providing request/response via JSON documents.


First time setup
----------------

	$ ./mkdb.sh

Running the server
------------------

	$ python3 dns-server.py



API
===

1. List DNS domains
-------------------
Show DNS domains, e.g. "example.com", available for use at this service.

HTTP URI: GET /domains

Params:

	None

Result:

	application/json document with the following data:
	List of domains (string)
	(or an HTTP 4xx, 5xx error)

Pricing:

	Free



2. Register host name
---------------------
HTTP URI: POST /host.register

Params:

	In HTTP body, a application/json document containing the following keys:

	name: name to register. Must be valid DNS name.
	pkh: (optional) public key hash for permissioned updates
	days: (optional) number of days to keep name registered (1-365)
	hosts: (optional) list of objects whose keys are:
		ttl: DNS TTL, in seconds
		rec_type: DNS record type ('A' and 'AAAA' supported)
		address: IPv4 or IPv6 address

Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:

	1000 satoshis



3. Update host records
----------------------
Replace _all_ DNS records associated a host, with the specified list.  An
empty list deletes all records.

HTTP URI: POST /host.update

Params:

	In HTTP body, a application/json document containing the following keys:

	name: name to register. Must be valid DNS name.
	pkh: public key hash for permissioned updates
	hosts: (optional) list of objects whose keys are:
		ttl: DNS TTL, in seconds
		rec_type: DNS record type ('A' and 'AAAA' supported)
		address: IPv4 or IPv6 address

	Header X-Bitcoin-Sig contains signature of encoded json document.

Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:

	1000 satoshis



4. Delete host
--------------
Replace _all_ DNS records associated a host, as well as the host itself.

HTTP URI: POST /host.delete

Params:

	In HTTP body, a application/json document containing the following keys:

	name: name to register. Must be valid DNS name.
	pkh: public key hash for permissioned updates

	Header X-Bitcoin-Sig contains signature of encoded json document.

Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:

	1000 satoshis



