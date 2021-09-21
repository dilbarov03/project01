#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database - DONE!✅✅✅

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
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
		shows = db.relationship('Show', backref="venue", lazy=True)


class Artist(db.Model):

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
		shows = db.relationship('Show', backref="artist", lazy=True)


class Show(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		artist_id = db.Column(db.Integer, db.ForeignKey(
				'artist.id'), nullable=False)
		venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
		start_time = db.Column(db.DateTime, nullable=False)



#db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)

	if format == 'full':
			format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
			format="EE MM, dd, y h:mma"
	else:
		format="EEEE MMMM, d, y 'at' h:mma"
	return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
	return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	data1 = Venue.query.all()

	return render_template('pages/venues.html', areas=data1);

@app.route('/venues/search', methods=['POST'])
def search_venues():
	search_term = request.form.get('search_term', '')
	search_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
	info = []

	for result in search_result:
		info.append({
			"id": result.id,
			"name": result.name,
			"num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all())
			})

	response={
		"count": len(search_result),
		"data": info
	}
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	venue = Venue.query.get(venue_id)

	if not venue:
		return render_template('errors/404.html')

	upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
	upcoming_shows = []

	past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
	past_shows = []

	for show in past_shows_query:
		past_shows.append({
			"artist_id": show.artist_id,
			"artist_name": show.artist.name,
			"artist_image_link": show.artist.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
		})

	for show in upcoming_shows_query:
		upcoming_shows.append({
			"artist_id": show.artist_id,
			"artist_name": show.artist.name,
			"artist_image_link": show.artist.image_link,
			"start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
		})

	data = {
		"id": venue.id,
		"name": venue.name,
		"genres": venue.genres,
		"address": venue.address,
		"city": venue.city,
		"state": venue.state,
		"phone": venue.phone,
		"website": venue.website_link,
		"facebook_link": venue.facebook_link,
		"seeking_talent": venue.seeking_talent,
		"seeking_description": venue.seeking_description,
		"image_link": venue.image_link,
		"past_shows": past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}

	return render_template('pages/show_venue.html', venue=data)
 
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST', 'GET'])
def create_venue_submission():
	try:
		name = request.form['name']
		city = request.form['city']
		state = request.form['state']
		address = request.form['address']
		phone = request.form['phone']
		image_link = request.form['image_link']
		genres = request.form.getlist('genres')
		facebook_link = request.form['facebook_link']
		website_link = request.form['website_link']
		seeking_talent = request.form['seeking_talent']
		seeking_talent = True if seeking_talent=="y" else False
		seeking_description = request.form['seeking_description']
		# TODO: insert form data as a new Venue record in the db, instead
		# TODO: modify data to be the data object returned from db insertion

		venue = Venue(
			name=name,
			city=city,
			state=state,
			address=address,
			phone=phone,
			image_link=image_link,
			genres=genres,
			facebook_link=facebook_link,
			website_link=website_link,
			seeking_talent=seeking_talent,
			seeking_description=seeking_description)
		# on successful db insert, flash success
		db.session.add(venue)
		db.session.commit()
		flash('Venue ' + request.form['name'] + ' was successfully listed!')

		return render_template('pages/home.html')
	except:
		flash('Error! Venue can not be listed!')

		return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')
    


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	data = Artist.query.all()
	
	return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	search_term = request.form.get('search_term', '')
	search_result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
	info = []

	for result in search_result:
		info.append({
			"id": result.id,
			"name": result.name,
			"num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all())
			})

	response={
		"count": len(search_result),
		"data": info
	}
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	artist_query = db.session.query(Artist).get(artist_id)

	if not artist_query: 
		return render_template('errors/404.html')

	past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
	past_shows = []

	for show in past_shows_query:
		past_shows.append({
			"venue_id": show.venue_id,
			"venue_name": show.venue.name,
			"artist_image_link": show.venue.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
		})

	upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
	upcoming_shows = []

	for show in upcoming_shows_query:
		upcoming_shows.append({
			"venue_id": show.venue_id,
			"venue_name": show.venue.name,
			"artist_image_link": show.venue.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
		})


	data = {
		"id": artist_query.id,
		"name": artist_query.name,
		"genres": artist_query.genres,
		"city": artist_query.city,
		"state": artist_query.state,
		"phone": artist_query.phone,
		"website_link": artist_query.website_link,
		"facebook_link": artist_query.facebook_link,
		"seeking_venue": artist_query.seeking_venue,
		"seeking_description": artist_query.seeking_description,
		"image_link": artist_query.image_link,
		"past_shows": past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}

	return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	artist = Artist.query.get(artist_id)
	if artist: 
		form.name.data = artist.name
		form.city.data = artist.city
		form.state.data = artist.state
		form.phone.data = artist.phone
		form.genres.data = artist.genres
		form.facebook_link.data = artist.facebook_link
		form.image_link.data = artist.image_link
		form.website_link.data = artist.website_link
		form.seeking_venue.data = artist.seeking_venue
		form.seeking_description.data = artist.seeking_description
	
	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	try:
		artist = Artist.query.get(artist_id)
		artist.name = request.form['name']
		artist.city = request.form['city']
		artist.state = request.form['state']
		artist.phone = request.form['phone']
		artist.genres = request.form.getlist('genres')
		artist.facebook_link = request.form['facebook_link']
		artist.image_link = request.form['image_link']
		artist.website_link = request.form['website_link']
		artist.seeking_venue = True if 'seeking_venue' in request.form else False 
		artist.seeking_description = request.form['seeking_description']

		db.session.commit()
		flash('Artist ' + request.form['name'] + ' was successfully edited!')
		return redirect(url_for('show_artist', artist_id=artist_id))
	except:
		flash('Error! Artist can not be edited!')

	finally:
		return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue = Venue.query.get(venue_id)
	
	if venue: 
		form.name.data = venue.name
		form.city.data = venue.city
		form.state.data = venue.state
		form.phone.data = venue.phone
		form.address.data = venue.address
		form.genres.data = venue.genres
		form.facebook_link.data = venue.facebook_link
		form.image_link.data = venue.image_link
		form.website_link.data = venue.website_link
		form.seeking_talent.data = venue.seeking_talent
		form.seeking_description.data = venue.seeking_description
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	try:
		venue = Venue.query.get(venue_id)
		venue.name = request.form['name']
		venue.city = request.form['city']
		venue.state = request.form['state']
		venue.address = request.form['address']
		venue.phone = request.form['phone']
		venue.image_link = request.form['image_link']
		venue.genres = request.form.getlist('genres')
		venue.facebook_link = request.form['facebook_link']
		venue.website_link = request.form['website_link']
		venue.seeking_talent = True if 'seeking_talent' in request.form else False 
		venue.seeking_description = request.form['seeking_description']

		db.session.commit()
		flash('Venue ' + request.form['name'] + ' was successfully edited!')

		return redirect(url_for('show_venue', venue_id=venue_id))
	except:
		flash('Error! Venue can not be edited!')

		return redirect(url_for('show_venue', venue_id=venue_id))


	

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
		name = request.form['name']
		city = request.form['city']
		state = request.form['state']
		phone = request.form['phone']
		image_link = request.form['image_link']
		genres = request.form.getlist('genres')
		facebook_link = request.form['facebook_link']
		website_link = request.form['website_link']
		seeking_venue = request.form['seeking_venue']
		seeking_venue = True if seeking_venue=="y" else False
		seeking_description = request.form['seeking_description']

		artist = Artist(
			name=name,
			city=city,
			state=state,
			phone=phone,
			image_link=image_link,
			genres=genres,
			facebook_link=facebook_link,
			website_link=website_link,
			seeking_venue=seeking_venue,
			seeking_description=seeking_description)
		# on successful db insert, flash success
		db.session.add(artist)
		db.session.commit()
		flash('Artist ' + request.form['name'] + ' was successfully listed!')

		return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

	shows_query = db.session.query(Show).join(Artist).join(Venue).all()

	data = []
	for show in shows_query: 
		data.append({
			"venue_id": show.venue_id,
			"venue_name": show.venue.name,
			"artist_id": show.artist_id,
			"artist_name": show.artist.name, 
			"artist_image_link": show.artist.image_link,
			"start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
		})

	return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	try:
		artist_id = request.form['artist_id']
		venue_id = request.form['venue_id']
		start_time = request.form['start_time']
		show = Show(
			artist_id=artist_id,
			venue_id=venue_id,
			start_time=start_time)
		db.session.add(show)
		db.session.commit()
		flash('Show was successfully listed!')
	except:
		flash('Error, show can not be created!')
	finally:
		return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
		return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
		return render_template('errors/500.html'), 500


if not app.debug:
		file_handler = FileHandler('error.log')
		file_handler.setFormatter(
				Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
		)
		app.logger.setLevel(logging.INFO)
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)
		app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
		app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
		port = int(os.environ.get('PORT', 5000))
		app.run(host='0.0.0.0', port=port)
'''
