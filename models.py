from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    release_date = db.Column(db.Date)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.String(256))
    streaming_services = db.Column(db.JSON)
    ratings = db.relationship('Rating', backref='movie', lazy='dynamic')

class TVShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    first_air_date = db.Column(db.Date)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.String(256))
    streaming_services = db.Column(db.JSON)
    ratings = db.relationship('Rating', backref='tv_show', lazy='dynamic')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    tv_show_id = db.Column(db.Integer, db.ForeignKey('tv_show.id'))
    media_type = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        db.CheckConstraint('score >= 0 AND score <= 10', name='check_valid_score'),
        db.CheckConstraint('(movie_id IS NOT NULL AND tv_show_id IS NULL) OR (movie_id IS NULL AND tv_show_id IS NOT NULL)', name='check_media_type'),
    )
