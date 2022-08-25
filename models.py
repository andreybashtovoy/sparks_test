from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    access_level = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<User %r>' % self.username


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    dt = db.Column(db.DateTime, default=datetime.now())


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    details_link = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256), nullable=True)
    image_link = db.Column(db.String(256), nullable=True)
    seller_name = db.Column(db.String(256), nullable=True)
    price = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
