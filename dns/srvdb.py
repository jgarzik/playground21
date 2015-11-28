
import apsw

class SrvDb(object):
    def __init__(self, filename):
        self.connection = apsw.Connection(filename)

    def domains(self):
        cursor = self.connection.cursor()
        rows = []
        for row in cursor.execute("SELECT name FROM domains ORDER BY name"):
            rows.append(row[0])
        return rows

