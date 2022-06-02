#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate


from models import db, Artist, Venue, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#db = SQLAlchemy(app)

# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['WTF_CSRF_ENABLED']
app.config['WTF_CSRF_CHECK_DEFAULT']

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#





#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by('id').limit(10)
  artists = Artist.query.order_by('id').limit(10)

  data = []
  artists_list = []
  venues_list = []
  for artist in artists:
      artists_list.append({
          "id": artist.id,
          "name": artist.name
      })
  for venue in venues:
      venues_list.append({
          "id": venue.id,
          "name": venue.name
      })
  data.append({
      "artists" : artists_list,
      "venues" : venues_list
      })

  #print(data)

  return render_template('pages/home.html', data=data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  venues = Venue.query.order_by('city', 'state').all()
  data = []
  today = datetime.today()
  cities =[]
  for venue in venues:
      city = venue.city.lower()
      if city not in cities:
              cities.append(city)
  for city in cities:
      venue_list = []
      state =''
      for venue in venues:
          if venue.city.lower() == city:
              state = venue.state
              city_name = venue.city
              sum = 0
              upcoming_shows=[]
              for show in venue.shows:
                  if show.start_time >= today:
                      sum += 1
                      upcoming_shows.append(show)
              venue_item ={
              "id" :venue.id,
              "name":venue.name,
              "upcoming_shows": upcoming_shows,
              "num_upcoming_shows": sum
              }
              venue_list.append(venue_item)
      area = {
          "city" : city_name,
          "state" : state,
          "venues" : venue_list
          }
      data.append(area)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '').strip()
  if ',' in search_term:
      search_items = search_term.split(',')
      city = search_items[0]
      venues = Venue.query.filter(city=city).all()
  else:
      venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  data = []
  today = datetime.today()
  for i in venues:
      sum = 0
      for show in i.shows:
          if show.start_time > today:
              sum += 1
      venue = {
          "id": i.id,
          "name": i.name,
          "num_upcoming_shows": sum
      }
      data.append(venue)
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)
  venue.genres = json.loads(venue.genres)
  today = datetime.now()
  if venue:
      phone = (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:])
      #upcoming_shows = []
      #past_shows = []
      upcoming_shows = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time > today).all()
      past_shows = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time < today).all()
      #print(past_shows1)
      #print(upcoming_shows1)
      for show in past_shows:
          artist = Artist.query.get(show.artist_id)
          show.artist_image_link = artist.image_link
          show.artist_name = artist.name
          show.start_time = format_datetime(str(show.start_time))
      for show in upcoming_shows:
          artist = Artist.query.get(show.artist_id)
          show.artist_image_link = artist.image_link
          show.artist_name = artist.name
          show.start_time = format_datetime(str(show.start_time))
      #for show in venue.shows:
          #artist = Artist.query.get(show.artist_id)
          #show.artist_image_link = artist.image_link
          #show.artist_name = artist.name
          #if show.start_time >= today:
              #show.start_time = format_datetime(str(show.start_time))
              #upcoming_shows.append(show)
              #print(upcoming_shows)
          #else:
              #show.start_time = format_datetime(str(show.start_time))
              #past_shows.append(show)
              #print(past_shows)


      venue.past_shows = past_shows
      venue.upcoming_shows = upcoming_shows
      venue.past_shows_count = len(past_shows)
      venue.upcoming_shows_count = len(upcoming_shows)
      return render_template('pages/show_venue.html', venue=venue)
  else:
      return render_template('errors/404.html')



#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

   form = VenueForm()
   name = form.name.data
   city = form.city.data
   state = form.state.data
   address = form.address.data
   phone = form.phone.data.strip('-')
   genres = json.dumps(form.genres.data)
   facebook_link = form.facebook_link.data
   image_link = form.image_link.data
   website = form.website_link.data
   seeking_talent = form.seeking_talent.data
   seeking_description = form.seeking_description.data
   if form.validate():
        error = False
        try:
            venue = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description, genres=genres)
            db.session.add(venue)
            db.session.commit()
        except():
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
             flash('An error occurred. Venue ' + name + ' could not be listed!')
             abort(500)
        else:
            flash('Venue ' + name + ' was successfully listed!')
            return redirect(url_for('index'))
   else:
        flash(form.errors)
        return redirect(url_for('create_venue_submission'))


@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):

  venue = Venue.query.get(venue_id)
  shows =Shows.query.all()

  venue_name = venue.name
  error = False
  try:
      for show in shows:
          if show.venue_id == venue_id:
              db.session.delete(show)
      db.session.delete(venue)
      db.session.commit()
  except():
      db.session.rollback()
      error =True
  finally:
      db.session.close()
  if error:
      abort(500)
      flash('An error occured deleting the Venue ' + venue_name + ' was successfully listed!')
  else:
      flash('The Venue ' + venue_name + ' was successfully deleted!')
      return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.order_by('id').all()
  data=[]
  for artist in artists:
      data.append({
          "id": artist.id,
          "name": artist.name
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').strip()
  if ',' in search_term:
      search_items = search_term.split(',')
      city = search_items[0]
      artists = Artist.query.filter(city=city).all()
  else:
      artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  data = []
  today = datetime.now()
  for i in artists:
      sum = 0
      for show in i.shows:
          if show.start_time > today:
              sum += 1
      artist = {
          "id": i.id,
          "name": i.name,
          "num_upcoming_shows": sum
      }
      data.append(artist)
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  artist.genres = json.loads(artist.genres)
  today = datetime.today()
  if artist:
      phone = (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:])
      #upcoming_shows = []
      #past_shows = []

      #for show in artist.shows:
          #venue = Venue.query.get(show.venue_id)
          #show.venue_image_link = venue.image_link
          #show.venue_name = venue.name
          #if show.start_time >= today:
              #show.start_time = format_datetime(str(show.start_time))
              #upcoming_shows.append(show)
          #else:
              #show.start_time = format_datetime(str(show.start_time))
              #past_shows.append(show)
      upcoming_shows = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time > today).all()
      past_shows = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time < today).all()
      #print(past_shows1)
      #print(upcoming_shows1)
      for show in past_shows:
          venue = Venue.query.get(show.venue_id)
          show.venue_image_link = venue.image_link
          show.venue_name = venue.name
          show.start_time = format_datetime(str(show.start_time))
      for show in upcoming_shows:
          venue = Venue.query.get(show.venue_id)
          show.venue_image_link = venue.image_link
          show.venue_name = venue.name
          show.start_time = format_datetime(str(show.start_time))

      artist.past_shows = past_shows
      artist.upcoming_shows = upcoming_shows
      artist.past_shows_count = len(past_shows)
      artist. upcoming_shows_count = len(upcoming_shows)
      return render_template('pages/show_artist.html', artist=artist)
  else:
      return render_template('errors/404.html')
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
      phone = (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:])
      form.name.data = artist.name
      form.city.data = artist.city
      form.state.data = artist.state
      form.phone.data = phone
      form.facebook_link.data = artist.facebook_link
      form.website_link.data = artist.website
      form.image_link.data = artist.image_link
      form.genres.data = json.loads(artist.genres)
      return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
      return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data.strip('-')
    genres = json.dumps(form.genres.data)
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    if form.validate():
         error = False
         try:
             artist = Artist.query.get(artist_id)

             artist.name = name
             artist.city = city
             artist.state = state
             artist.phone = phone
             artist.facebook_link = facebook_link
             artist.image_link = image_link
             artist.website = website
             artist.seeking_venue = seeking_venue
             artist.seeking_description = seeking_description
             artist.genres = genres

             db.session.add(artist)
             db.session.commit()
         except():
             error = True
             db.session.rollback()

         finally:
             db.session.close()
         if error:
              flash('An error occurred. Artist ' + name + ' could not be Updated!')
              abort(500)
         else:
             flash('Artist ' + name + ' was successfully Updated!')
             return redirect(url_for('show_artist', artist_id=artist_id))
    else:
         flash(form.errors)
         return redirect(url_for('edit_artist_submission', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue:
      phone = (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:])
      form.name.data = venue.name
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = phone
      form.address.data = venue.address
      form.facebook_link.data = venue.facebook_link
      form.website_link.data = venue.website
      form.image_link.data = venue.image_link
      form.genres.data = json.loads(venue.genres)
      return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
      return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data.strip('-')
  genres = json.dumps(form.genres.data)
  facebook_link = form.facebook_link.data
  image_link = form.image_link.data
  website = form.website_link.data
  seeking_talent = form.seeking_talent.data
  seeking_description = form.seeking_description.data

  if form.validate():
       error = False
       try:
           venue = Venue.query.get(venue_id)

           venue.name = name
           venue.city = city
           venue.state = state
           venue.phone = phone
           venue.address = address
           venue.facebook_link = facebook_link
           venue.image_link = image_link
           venue.website = website
           venue.seeking_talent = seeking_talent
           venue.seeking_description = seeking_description
           venue.genres = genres

           db.session.add(venue)
           db.session.commit()
       except():
           error = True
           db.session.rollback()

       finally:
           db.session.close()
       if error:
            flash('An error occurred. Venue ' + name + ' could not be Updated!')
            abort(500)
       else:
           flash('Venue ' + name + ' was successfully Updated!')
           return redirect(url_for('show_venue', venue_id=venue_id))
  else:
       flash(form.errors)
       return redirect(url_for('edit_venue_submission', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data.strip('-')
    genres = json.dumps(form.genres.data)
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    if form.validate():
       error = False
       try:
           artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description, genres=genres)

           db.session.add(artist)
           db.session.commit()
       except():
           error = True
           db.session.rollback()

       finally:
           db.session.close()
       if error:
            flash('An error occurred. Artist ' + name + ' could not be listed!')
            abort(500)
       else:
           flash('Artist ' + name + ' was successfully listed!')
           return redirect(url_for('index'))
    else:
       flash(form.errors)
       return redirect(url_for('create_artist_submission'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Shows.query.all()
  data =[]
  for show in shows:
      showItem = {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
          }
      data.append(showItem)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create',  methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()

    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    if form.validate():
         error = False
         try:
             show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
             db.session.add(show)
             db.session.commit()
         except():
             error = True
             db.session.rollback()

         finally:
             db.session.close()
         if error:
              flash('An error occurred. Show could not be listed.')
              abort(500)
         else:
             flash('Show was successfully listed!')
             return redirect(url_for('index'))
    else:
         flash(form.errors)
         return redirect(url_for('create_show_submission'))


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
