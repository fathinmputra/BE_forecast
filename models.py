# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class PriceData(db.Model):
    __tablename__ = 'prices'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
