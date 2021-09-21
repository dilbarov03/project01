from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Venue(db.Model):
	__tablename__ = 'venue'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	genres = db.Column(db.ARRAY(db.String()))
	address = db.Column(db.String(120))
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))
	website_link = db.Column(db.String(120))
	seeking_talent = db.Column(db.Boolean, default=False)
	seeking_description = db.Column(db.String(500))
	shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")


class Artist(db.Model):
	__tablename__ = 'artist'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	genres = db.Column(db.ARRAY(db.String))
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	website_link = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))
	seeking_venue = db.Column(db.Boolean)
	seeking_description = db.Column(db.String(500), default=False)
	shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")


class Show(db.Model):
	__tablename__ = 'show'
	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey(
			'artist.id'), nullable=False)
	venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
	start_time = db.Column(db.DateTime, nullable=False)
