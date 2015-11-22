# causeway
 
A storage service geared toward small files with ECDSA signature auth that works with the 21 Bitcoin Computer

This project is for a server that will store and return data for a certain amount of time and accept updates if they are signed by a user's payment address.

## REST API

* All requests via HTTP GET except where noted.
* Data returned as JSON, formatted with indent=4 for now.

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

### /price
    Parameters
        None
        
    Returns
        price - satoshis for 1 MB storage + 50 MB transfer

### /nonce
    Parameters
        address - account requesting a nonce
        
    Returns
        nonce - random 32-byte string
        
Note: nonce will later be stored until used or next nonce generated for address

***
** Roadmap **

* All storage expires after one year. Extended by uploading the same data. 
* Data is kept if bandwidth is exceeded just no longer served until balance is increased.
    
### /address
    Parameters
        contact - email or Bitmessage address to contact on expiration
        address - account this will be used to fund
        signature - signature for concatenation of contact and address by
            private key for address
        
    Returns
        address - a new, unused Bitcoin address


### /balance
    Parameters
        address - account on which to report balance
        nonce - latest unused 32-byte string retrieved via /nonce
        signature - signature over concat(address and last nonce received via /nonce call)
        
    Returns
        balance - satoshis worth of value left on account

### /get
    Parameters
        key - used to retrieve value
        
    Returns
        key - the key that was requested
        value - the last value stored for the key
        
Note: Charges bandwidth against key/value submitter's account.
        
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
            Possible error reasons
