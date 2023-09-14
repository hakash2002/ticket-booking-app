from application.database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=True)
    id = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    admin_no = db.Column(db.Integer, db.ForeignKey(
        'admin.admin_no'), default=None)
    bookings = db.relationship('Userbooking', backref='user')


class Venue(db.Model):
    __tablename__ = 'venue'
    venue_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    place = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    admin_no = db.Column(db.Integer, db.ForeignKey(
        'admin.admin_no'), nullable=False)
    shows = db.relationship('Show', backref='venue')


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    admin_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    venue = db.relationship('Venue', backref='admin',
                            cascade='all, delete-orphan')


class Show(db.Model):
    __tablename__ = 'show'
    show_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    tags = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    venue_no = db.Column(db.Integer, db.ForeignKey(
        'venue.venue_no'), nullable=False)
    admin_no = db.Column(db.Integer, db.ForeignKey(
        'admin.admin_no'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    ratings = db.relationship('Rating', backref='show', lazy=True)
    admin_rate = db.Column(db.Float, nullable=True)


class Userbooking(db.Model):
    __tablename__ = 'userbooking'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_no = db.Column(db.Integer, db.ForeignKey(
        'user.user_no'), nullable=False)
    show_no = db.Column(db.Integer, db.ForeignKey(
        'show.show_no'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Rating(db.Model):
    __tablename__ = 'rating'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_no = db.Column(db.Integer, db.ForeignKey(
        'user.user_no'), nullable=False)
    show_no = db.Column(db.Integer, db.ForeignKey(
        'show.show_no'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

