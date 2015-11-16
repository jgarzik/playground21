
import apsw


connection = apsw.Connection("apibb.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE names(name TEXT PRIMARY KEY, created INTEGER, expires INTEGER)")
cursor.execute("CREATE TABLE ads(name TEXT, uri TEXT, pubkey TEXT, created INTEGER, expires INTEGER)")

