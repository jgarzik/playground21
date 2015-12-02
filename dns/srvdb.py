
import apsw
import time

class SrvDb(object):
    def __init__(self, filename):
        self.connection = apsw.Connection(filename)

    def valid_domain(self, domain):
        cursor = self.connection.cursor()

        row = cursor.execute("SELECT COUNT(*) FROM domains WHERE name = ?", (domain,)).fetchone()
        if not row or (int(row[0] < 1)):
            return False
        return True

    def domains(self):
        cursor = self.connection.cursor()

        # retrieve sorted domain list
        rows = []
        for row in cursor.execute("SELECT name FROM domains ORDER BY name"):
            rows.append(row[0])
        return rows

    def add_host(self, name, domain, days, pkh):
        cursor = self.connection.cursor()

        # Create, expiration times
        tm_creat = int(time.time())
        tm_expire = tm_creat + (days * 24 * 60 * 60)

        # Add hash metadata to db
        cursor.execute("INSERT INTO hosts VALUES(?, ?, ?, ?, ?)", (name, domain, tm_creat, tm_expire, pkh))

        return True

    def get_host(self, name, domain):
        cursor = self.connection.cursor()

        curtime = int(time.time())
        row = cursor.execute("SELECT * FROM hosts WHERE name = ? AND domain = ? AND time_expire > ?", (name, domain, curtime)).fetchone()
        if not row:
            return None
        obj = {
            'name': row[0],
            'domain': row[1],
            'create': int(row[2]),
            'expire': int(row[3]),
            'pkh': row[4],
        }
        return obj

    def update_records(self, name, domain, host_records):
        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM records WHERE name = ? AND domain = ?", (name, domain))

        for host_rec in host_records:
            cursor.execute("INSERT INTO records VALUES(?, ?, ?, ?, ?)", host_rec)

    def delete_host(self, name, domain):
        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM records WHERE name = ? AND domain = ?", (name, domain))
        cursor.execute("DELETE FROM hosts WHERE name = ? AND domain = ?", (name, domain))

