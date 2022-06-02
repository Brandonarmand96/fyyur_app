
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='venue', lazy='select')
    genres = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f' <Venue: {self.id}, name: {self.name}, city: {self.city}, state:{self.state}, address:{self.address}, phone:{self.phone}, image: {self.image_link}, facebook:{self.facebook_link}, website: {self.website}, genres: {self.genres}, seeking_talent:{self.seeking_talent}, seeking_description:{self.seeking_description}>'


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='artist', lazy='select')
    genres = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f' <Artist: {self.id}, name: {self.name}, city: {self.city}, state:{self.state}, address:{self.address}, phone:{self.phone}, image: {self.image_link}, facebook:{self.facebook_link}, website: {self.website}, genres: {self.genres}, seeking_venue:{self.seeking_venue}, seeking_description:{self.seeking_description}>'


class Shows(db.Model):
    __tablename__="show"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f' <Show: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}>'
