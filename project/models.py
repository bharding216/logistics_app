from . import db
# from the current package (which is 'project')
# import the db variable

from flask_login import UserMixin
from sqlalchemy.sql import func


class appts_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Integer)
    material = db.Column(db.String(10))
    pickup_date = db.Column(db.String(10))
    pickup_time = db.Column(db.String(5))
    PO_number = db.Column(db.String(30))


class carriers_db(db.Model):
    carrier_id = db.Column(db.Integer, primary_key=True)
    carrier_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15))


class log_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modified_on = db.Column(db.DateTime, default=func.now())
    action = db.Column(db.String(7))
    carrier = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Integer)
    material = db.Column(db.String(10))
    pickup_date = db.Column(db.String(10))
    pickup_time = db.Column(db.String(5))
    PO_number = db.Column(db.String(30))


class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    access_ranking = db.Column(db.Integer)

# Access Ranking Descriptions:
# 1 => can only view schedule
# 2 => ** placeholder for future use **
# 3 => no restrictions



