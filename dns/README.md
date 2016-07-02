
dns - Dynamic DNS management service
====================================

Summary:  Dynamic DNS domain management system

Once connected to your BIND9 DNS servers, this server enables you to
monetize your domain by selling 

	YOUR-NAME-HERE.example.com

Customers buy "my-silly-name.example.com" from this service,
and control all DNS address records under that DNS domain.

Demonstrates:

* Pricing in USD dollars (converted to satoshis)

* Flask error handling, file upload.

* Public key authentication - Remote client provides public key from a 21
  wallet.  Server verifies signature before updating records.

* Permissioned SQL database access.

* Providing request/response via JSON documents.

Status: Tested and feature complete client + server.

First time setup
----------------

	$ ./mkdb.sh

Running the server
------------------

	$ python3 dns-server.py



API
===

0. Show endpoint API metadata
-----------------------------
HTTP URI: GET /

Params:

	None

Result:

	application/json document with standard API endpoint descriptors.

Example:

	[ {
	    "name": "dns/1",
	    "website": "https://github.com/jgarzik/playground21/tree/master/dns",
	    "pricing": [
	      {
	        "rpc": "domains",
	        "per-req": 0
	      },
	      {
	        "rpc": "host.register",
	        "per-day": 56
	      },
	      {
	        "rpc": "simpleRegister",
	        "per-day": 56
	      },
	      {
	        "rpc": "records.update",
	        "per-req": 564
	      },
	      {
	        "rpc": "host.delete",
	        "per-req": 0
	      }
	    ],
	    "pricing-type": "per-rpc"
	} ]


1. List DNS domains
-------------------
Show DNS domains, e.g. "example.com", available for use at this service.

HTTP URI: GET /dns/1/domains

Params:

	None

Result:

	application/json document with the following data:
	List of domains (string)
	(or an HTTP 4xx, 5xx error)

Pricing:

	Free

Example:

	[
  		"example.com",
  		"bcapi.xyz"
	]


2. Register host name
---------------------
HTTP URI: POST /dns/1/host.register

Params:

	In HTTP body, a application/json document containing the following keys:

	name: name to register. Must be valid DNS name.
	domain: domain name under which name will be registered
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

	US$0.0002/day

Example:

	{
		"name": "test3",
		"domain": "example.com",
		"pkh": "1M3iEX7daqd9psQC8PsxN7ZE3GjoAe6k7d",
		"days": 1,
		"hosts": [
			{"ttl": 30, "address": "127.0.0.1", "rec_type": "A"}
		]
	}


3. Update host records
----------------------
Replace _all_ DNS records associated a host, with the specified list.  An
empty list deletes all records.

HTTP URI: POST /dns/1/records.update

Params:

	In HTTP body, a application/json document containing the following keys:

	name: name to register. Must be valid DNS name.
	domain: domain name under which name will be registered
	hosts: (optional) list of objects whose keys are:
		ttl: DNS TTL, in seconds
		rec_type: DNS record type ('A' and 'AAAA' supported)
		address: IPv4 or IPv6 address

	Header X-Bitcoin-Sig contains signature of encoded json document, signed with key used in host.register.

Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:

	US$0.002

Example:

	{
	  "name": "test"
	  "domain": "example.com",
	  "hosts": [
	    {
	      "address": "127.0.0.1",
	      "ttl": 30,
	      "rec_type": "A"
	    },
	    {
	      "address": "::1",
	      "ttl": 60,
	      "rec_type": "AAAA"
	    }
	  ],
	}



4. Delete host
--------------
Remove _all_ DNS records associated a host, as well as the host itself.

HTTP URI: POST /dns/1/host.delete

Params:

	In HTTP body, a application/json document containing the following keys:

	name: name to register. Must be valid DNS name.
	domain: domain name under which name will be registered
	pkh: public key hash for permissioned updates

	Header X-Bitcoin-Sig contains signature of encoded json document, signed with key used in host.register.

Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:

	Free

Example:

	{
	  "domain": "example.com",
	  "name": "test3",
	  "pkh": "1M3iEX7daqd9psQC8PsxN7ZE3GjoAe6k7d"
	}


5. Register host name (simplified interface)
--------------------------------------------
HTTP URI: GET /dns/1/simpleRegister

Params:

	HTTP query string parameters:

	name: name to register. Must be valid DNS name.
	domain: domain name under which name will be registered
	days: Number of days to register
	ip: IPv4 or IPv6 address (e.g. 127.0.0.1)

Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:

	US$0.0002/day

Example:

Register **test2.example.com** for **4** days at address **127.0.0.1**.

	GET /dns/1/simpleRegister?name=test2&domain=example.com&days=4&ip=127.0.0.1

