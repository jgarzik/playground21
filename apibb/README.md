
apibb - API bulletin board - rendezvous service
===============================================

Summary
-------
There exists a top-level namespace of DNS-like names (valid chars: A-Z,-.),
where each name is a container for many node advertisements.

NAMES
-----
* List of names costs 1 satoshi.
* Names cost 10 satoshis/hour to exist, after which they are removed.
* Anyone may pay to extend the lifetime of a name, for up to 30 days.

ADVERTISEMENTS
--------------
* List of advertisements contained within one name costs 1 satoshi.
* Advertisements cost 2 satoshis/hour to exist, after which they are removed.

Other notes
-----------
* A node may advertise their service URI within a single name for X hours
* All names, and all advertisements expire (if not extended w/ payment)
* Example:  Nodes seeking storage services download a list of all nodes
    advertising the "storage.v1" service.

Pricing theory
--------------
(A) Anybody may pay to create or renew a name for X hours.

(B) Anybody may pay to advertise a name + URI combination for X hours.


Example:

	"escrow.v1": [
		[ "http://192.25.0.1:14001", "public key" ],
		[ "http://88.92.0.3:14001", "public key 3" ],
	],
	"storage.v1": [
		[ "http://127.0.0.1:10101", "public key" ],
		[ "http://127.0.0.2:10101", "public key 2" ],
		[ "http://127.0.0.3:10101", "public key 3" ],
	],


Future Directions
-----------------
* Check public key before permitting advertisement to be extended
* If advertisements within a container exceeds 1,000, enable competitive
  bidding to remain within the container.



First time setup
----------------
$ python3 mkdb.py

This creates an empty apibb.db file used for backing storage.


Running the server
------------------
$ python3 apibb-server.py


API;

name-list = names()
name.renew(name, delta-hours)
ad-list = ads(name)
advertise(name, uri, pubkey, delta-hours)



1. Get list of names
--------------------

HTTP URI: /names

Params:
	none

Result:
	JSON list of objects containing: name, creation time, expiration time

Pricing:
	1 satoshi


2. Create a name / renew name
-----------------------------

HTTP URI: /namerenew

Params:
	name	Name string
	hours	Number of hours until expiration
		(or if renewing, number of hours to add to expiration)

Result if successful:
	Binary string, "OK"

Pricing:
	10 satoshis per hour


3. Show all nodes advertising a service
---------------------------------------

HTTP URI: /ads

Params:
	name	Name string

Result if successful:
	JSON list of objects, each obj describes a single node
	advertising the "name" service.

Pricing:
	1 satoshi


4. Advertise a service
----------------------

HTTP URI: /advertise

Params:
	name	Name string
	uri	URI to advertise
	pubkey	Public key associated with URI
	hours	Number of hours until expiration
		(or if renewing, number of hours to add to expiration)

Result if successful:
	Binary string, "OK"

Pricing:
	2 satoshis per hour

