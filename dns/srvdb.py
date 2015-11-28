
import apsw

class Srvdb(object):
    def __init__(self):
        pass

    def last_idx(cursor):
        row = cursor.execute("SELECT MAX(hd_index) FROM metadata").fetchone()
        if row is None:
            return 0
        return int(row[0])

    def insert(cursor, address, pubkey, next_idx, owner_b64):
        rv = True
        try:
            cursor.execute("INSERT INTO metadata VALUES(?, ?, ?, ?)", (address, pubkey, next_idx, owner_b64))
        except:
            rv = False
        return rv

