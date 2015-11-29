
import apsw
import time
import binascii
import json

class SrvDb(object):
    def __init__(self, filename):
        self.connection = apsw.Connection(filename)

    def worker_add(self, pkh, payout_addr):
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO workers VALUES(?, ?, 0, 0, 0)", (pkh, payout_addr))

    def task_add(self, id, summary, pkh, image, image_ctype, template, min_workers, reward):
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO tasks VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (id, summary, pkh, image, image_ctype, template, min_workers, reward))

    def tasks(self):
        cursor = self.connection.cursor()

        tasks = []
        for row in cursor.execute("SELECT id,summary,min_workers,reward FROM tasks"):
            obj = {
                'id': row[0],
                'summary': row[1],
                'min_workers': int(row[2]),
                'reward': int(row[3]),
            }
            tasks.append(obj)

        return tasks

    def task_get(self, id):
        cursor = self.connection.cursor()

        row = cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        if row is None:
            return None

        obj = {
            'summary': row[1],
            'pkh': row[2],
            'image': binascii.hexlify(row[3]).decode('utf-8'),
            'image_ctype': row[4],
            'template': json.loads(row[5]),
            'min_workers': int(row[6]),
            'reward': int(row[7]),
        }
        return obj

