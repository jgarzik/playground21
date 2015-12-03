
turk - Mechanical Turk service
==============================

WARNING:  Untested code ahead.  Needs lots of testing.

Summary:  API for automating and comparing work by human(?) workers.

How it works:

1. Supervisor submits an image, and a list of questions about an image.  A
minimum number of workers, and a bitcoin reward, is specified.

2. Workers download the image, answer the question(s), submit results.

3. API collects work.  When X workers have submitted answers, they are
compared for matches.  The most matches - most accurate - workers receive
the reward.


Status:  Final compare-work-and-perform-payouts step is UNTESTED.  All else works.


First time setup
----------------

	$ ./mkdb.sh

Running the server
------------------

	$ python3 turk-server.py



API
===

1. Get task to work on
----------------------

HTTP URI: GET /task/<id>

Params:


Result:


Pricing:




2. Submit work to supervisor
----------------------------
HTTP URI: POST /task

Params:

	In HTTP body, a application/json document containing the following keys:


Result:


Pricing:




3. Get list of tasks
----------------------

HTTP URI: GET /tasks.list

Params:

	None

Result:

	application/json document with the following data:
	(or an HTTP 4xx, 5xx error)

Pricing:




4. Supervisor creates new task to receive work
----------------------------------------------

HTTP URI: POST /task.new

Params:

	In HTTP body, a application/json document containing the following keys:


Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:


5. Register as new worker to receive tasks
------------------------------------------

HTTP URI: POST /worker.new

Params:

	In HTTP body, a application/json document containing the following keys:


Result:

	application/json document with the following data: true
	(or an HTTP 4xx, 5xx error)

Pricing:



