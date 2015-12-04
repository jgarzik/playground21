# causeway
 
A storage service geared toward small files with ECDSA signature auth that works with the 21 Bitcoin Computer

This project is for a server that will store and return data for a certain amount of time and accept updates if they are signed by a user's payment address.

## REST API

* All requests via HTTP GET except where noted.
* Data returned as JSON, formatted with indent=4 for now.

### /get
    Parameters
        key - used to retrieve value
        
    Returns
        key - the key that was requested
        value - the value stored for the key

Note: Charges bandwidth against sale record associated with key/value.

### /price
    Parameters
        None
        
    Returns
        price - satoshis for 1 MB storage + 50 MB transfer

### /buy
    Parameters
        contact - email address to notify on expiration
        address - owner of new hosting bucket

    Returns
        result - success or error
        buckets - listing free space, reamining bandwidth, and expiration

        
### /put (POST)
    Parameters
        key - string
        value - string
        address - account to charge for this data
        nonce - latest unused 32-byte string retrieved via /nonce
        signature - signature over concat(key + value + address + nonce) by 
            private key for address

    Returns
        status - "success" or "error: " + error reason

### /delete (POST)
    Parameters
        key - string
        address - account that owns this key
        nonce = latest unused 32-byte string retrieved via /nonce
        signature - signature over concat(key + address + nonce) by 
            private key for address

### /nonce
    Parameters
        address - manually entered account requesting a nonce, users will need to 
                  pay to register in order to be eligible for nonces
        
    Returns
        nonce - random 32-byte string
        
Note: nonce will later be stored until used or next nonce generated for address

### /help
    Parameters
        None

    Returns
        List of available endpoints

### /status
    Parameters
        None

    Returns
        uptime - time in seconds that the service has been running
        stored - bytes stored
        free - bytes free
        price - satoshis for 1 MB storage + 50 MB transfer


## Installation

### raspbian

First choose where you will host your database, this database will host operational as well as customer-uploaded data.

    sudo apt-get install python3-flask-sqlalchemy sqlite3
    sqlite3 /path/to/db/causeway.db < schema.sql

Then you'll need to copy default\_settings.py to settings.py and change DATABASE to the full path where you created the database.

***
** Roadmap **

* Hosting is purchased in buckets which expire after one month.
* A bucket holds 1 MB of data and comes with 50 MB of transfer.
* If a bucket expires, key/values are redistributed to an owner's newer buckets if possible,
  otherwise, the owner is notified via email that expiration is affecting hosting.
* Data is kept if bandwidth is exceeded just no longer served until more is purchased.

### /address
    Parameters
        contact - email or Bitmessage address to contact on expiration
        address - account this will be used to fund
        signature - signature for concatenation of contact and address by
            private key for address
        
    Returns
        address - a dummy string, later an address suitable for funding an account

### /balance
    Parameters
        address - account on which to report balance
        nonce - latest unused 32-byte string retrieved via /nonce
        signature - signature over concat(address and last nonce received via /nonce call)
        
    Returns
        balance - satoshis worth of value left on account

