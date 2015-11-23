
from settings import *

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)

class Owner(db.Model):
    __tablename__ = 'owner'
    address = db.Column(db.String(64), primary_key=True)
    nonce = db.Column(db.String(32), unique=True)
    balance = db.Column(db.Integer)
    bad_attempts = db.Column(db.Integer)

    def __init__(self, address, nonce=None, balance=0, bad_attempts=0):
        self.address = address
        self.nonce = nonce
        self.balance = balance
        self.bad_attempts = bad_attempts

    def __repr__(self):
        return '<Owner %r>' % self.address
