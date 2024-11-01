from app import db
from datetime import date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    rol = db.Column(db.String(10), default='CLIENTE', nullable=False)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False, default="")
    genre = db.Column(db.String(50), nullable=False, default="")
    added_date = db.Column(db.Date, default=date.today)
    available = db.Column(db.Boolean, default=True)
    cover_image = db.Column(db.String(255), nullable=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), default=None)