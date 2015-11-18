
import apsw


connection = apsw.Connection("keyvalue.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE tab(k BLOB PRIMARY KEY, v BLOB)")

