#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
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
import json
import dateutil.parser
import babel
from flask import (
	Flask, 
	render_template, 
	request, 
	Response, 
	flash, 
	redirect, 
	url_for)

from models import db, Venue, Artist, Show    


app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

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
	venue = Venue.query.get_or_404(venue_id)

	past_shows = []
	upcoming_shows = []

	for show in venue.shows:
			temp_show = {
					'artist_id': show.artist_id,
					'artist_name': show.artist.name,
					'artist_image_link': show.artist.image_link,
					'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
			}
			if show.start_time <= datetime.now():
					past_shows.append(temp_show)
			else:
					upcoming_shows.append(temp_show)

	# object class to dict
	data = vars(venue)

	data['past_shows'] = past_shows
	data['upcoming_shows'] = upcoming_shows
	data['past_shows_count'] = len(past_shows)
	data['upcoming_shows_count'] = len(upcoming_shows)

	return render_template('pages/show_venue.html', venue=data)
 
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm(request.form)
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST', 'GET'])
def create_venue_submission():
	try:
		form = VenueForm(request.form)
		venue = Venue(
			name=form.name.data,
			city=form.city.data,
			state=form.state.data,
			address=form.address.data,
			phone=form.phone.data,
			image_link=form.image_link.data,
			genres=form.genres.data,
			facebook_link=form.facebook_link.data,
			website_link=form.website_link.data,
			seeking_talent=form.seeking_talent.data,
			seeking_description=form.seeking_description.data)
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
			"venue_image_link": show.venue.image_link,
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
	form = ArtistForm(request.form)
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	form = ArtistForm(request.form)
	artist = Artist(
		name=form.name.data,
		city=form.city.data,
		state=form.state.data,
		phone=form.phone.data,
		image_link=form.image_link.data,
		genres=form.genres.data,
		facebook_link=form.facebook_link.data,
		website_link=form.website_link.data,
		seeking_venue=form.seeking_venue.data,
		seeking_description=form.seeking_description.data)

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
	form = ShowForm(request.form)
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	try:
		form = ShowForm(request.form)
		show = Show(
			artist_id=form.artist_id.data,
			venue_id=form.venue_id.data,
			start_time=form.start_time.data)
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
