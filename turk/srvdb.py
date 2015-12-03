
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

    def worker_inc_req(self, pkh):
        cursor = self.connection.cursor()

        cursor.execute("UPDATE workers SET tasks_req = tasks_req + 1 WHERE auth_pkh = ?", (pkh,))

    def worker_inc_done(self, pkh):
        cursor = self.connection.cursor()

        cursor.execute("UPDATE workers SET tasks_done = tasks_done + 1 WHERE auth_pkh = ?", (pkh,))

    def worker_get(self, pkh):
        cursor = self.connection.cursor()

        row = cursor.execute("SELECT * FROM workers WHERE auth_pkh = ?", (pkh,)).fetchone()
        if row is None:
            return None
        obj = {
            'pkh': pkh,
            'payout_addr': row[1],
            'tasks_req': int(row[2]),
            'tasks_done': int(row[3]),
            'tasks_accepted': int(row[4]),
        }
        return obj

    def task_add(self, id, summary, pkh, image, image_ctype, template, min_workers, reward):
        cursor = self.connection.cursor()

        tstamp = int(time.time())
        cursor.execute("INSERT INTO tasks VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, summary, pkh, image, image_ctype, template, min_workers, reward, tstamp))

    def task_close(self, id):
        cursor = self.connection.cursor()

        cursor.execute("UPDATE tasks SET time_closed=datetime('now') WHERE id = ?", (id,))

    def tasks(self):
        cursor = self.connection.cursor()

        tasks = []
        for row in cursor.execute("SELECT id,summary,min_workers,reward,time_create FROM tasks ORDER BY time_create DESC"):
            obj = {
                'id': row[0],
                'summary': row[1],
                'min_workers': int(row[2]),
                'reward': int(row[3]),
                'time_create': int(row[4]),
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
            'time_create': int(row[8]),
        }
        return obj

    def answer_add(self, id, pkh, answers):
        cursor = self.connection.cursor()

        tstamp = int(time.time())
        cursor.execute("INSERT INTO answers VALUES(?, ?, ?, ?)", (id, pkh, answers, tstamp))

    def answers_get(self, id):
        cursor = self.connection.cursor()

        answers = []
        for row in cursor.execute("SELECT * FROM answers WHERE id = ?", (id,)):
            obj = {
                'worker': row[1],
                'answers': json.loads(row[2]),
                'time_submit': int(row[3]),
            }
            answers.append(obj)

        return answers
