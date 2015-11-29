
import apsw
import time

class SrvDb(object):
    def __init__(self, filename):
        self.connection = apsw.Connection(filename)

    def worker_add(self, pkh, payout_addr):
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO workers VALUES(?, ?, 0, 0, 0)", (pkh, payout_addr))

    def task_add(self, id, pkh, image, image_ctype, questions, min_workers, reward):
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO tasks VALUES(?, ?, ?, ?, ?, ?, ?)", (id, pkh, image, image_ctype, questions, min_workers, reward))

