from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from models import User, Movie, TVShow, Rating
from forms import LoginForm, RegistrationForm, SearchForm, RatingForm
from tmdb_api import get_popular_movies, get_popular_tv_shows, search_multi, get_movie_details, get_tv_show_details, get_genres, get_similar_tv_shows
from datetime import datetime

main = Blueprint('main', __name__)

@main.app_template_filter('format_date')
def format_date(value, format='%B %d, %Y'):
    if value:
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    return ''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    popular_movies = get_popular_movies()['results'][:5]
    popular_tv_shows = get_popular_tv_shows(region='US', year=2024)['results'][:5]
    return render_template('index.html', movies=popular_movies, tv_shows=popular_tv_shows)

@main.route('/movies')
def movie_list():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre_id')
    popular_movies = get_popular_movies(page=page, genre_id=genre_id)
    genres = get_genres('movie')
    return render_template('movie_list.html', movies=popular_movies['results'], page=page, total_pages=popular_movies['total_pages'], genres=genres, current_genre_id=genre_id)

@main.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie_details = get_movie_details(movie_id)
    db_movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not db_movie:
        db_movie = Movie(
            tmdb_id=movie_id,
            title=movie_details['title'],
            release_date=datetime.strptime(movie_details['release_date'], '%Y-%m-%d').date() if movie_details['release_date'] else None,
            overview=movie_details['overview'],
            poster_path=movie_details['poster_path']
        )
        db.session.add(db_movie)
        db.session.commit()
    
    form = RatingForm()
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, movie_id=db_movie.id).first()
    
    return render_template('movie_detail.html', movie=movie_details, db_movie=db_movie, form=form, user_rating=user_rating)

@main.route('/tv_shows')
def tv_show_list():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre_id')
    year = request.args.get('year', 2024, type=int)
    popular_tv_shows = get_popular_tv_shows(page=page, genre_id=genre_id, region='US', year=year)
    genres = get_genres('tv')
    
    # Fetch additional details for each TV show
    for tv_show in popular_tv_shows['results']:
        details = get_tv_show_details(tv_show['id'])
        tv_show['number_of_seasons'] = details.get('number_of_seasons', 'N/A')
        tv_show['number_of_episodes'] = details.get('number_of_episodes', 'N/A')
    
    return render_template('tv_show_list.html', tv_shows=popular_tv_shows['results'], page=page, total_pages=popular_tv_shows['total_pages'], genres=genres, current_genre_id=genre_id, current_year=year)

@main.route('/tv_show/<int:tv_id>')
def tv_show_detail(tv_id):
    tv_show_details = get_tv_show_details(tv_id)
    db_tv_show = TVShow.query.filter_by(tmdb_id=tv_id).first()
    if not db_tv_show:
        db_tv_show = TVShow(
            tmdb_id=tv_id,
            name=tv_show_details['name'],
            first_air_date=datetime.strptime(tv_show_details['first_air_date'], '%Y-%m-%d').date() if tv_show_details['first_air_date'] else None,
            overview=tv_show_details['overview'],
            poster_path=tv_show_details['poster_path']
        )
        db.session.add(db_tv_show)
        db.session.commit()
    
    form = RatingForm()
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, tv_show_id=db_tv_show.id).first()
    
    similar_tv_shows = get_similar_tv_shows(tv_id)['results'][:5]
    
    return render_template('tv_show_detail.html', tv_show=tv_show_details, db_tv_show=db_tv_show, form=form, user_rating=user_rating, similar_tv_shows=similar_tv_shows)

@main.route('/rate/<string:media_type>/<int:media_id>', methods=['POST'])
@login_required
def rate_media(media_type, media_id):
    form = RatingForm()
    if form.validate_on_submit():
        if media_type == 'movie':
            db_media = Movie.query.filter_by(tmdb_id=media_id).first()
        elif media_type == 'tv':
            db_media = TVShow.query.filter_by(tmdb_id=media_id).first()
        else:
            flash('Invalid media type.')
            return redirect(url_for(f'main.{media_type}_detail', **{f'{media_type}_id': media_id}))
        
        if not db_media:
            flash('Media not found.')
            return redirect(url_for(f'main.{media_type}_detail', **{f'{media_type}_id': media_id}))
        
        rating = Rating.query.filter_by(user_id=current_user.id, movie_id=db_media.id if media_type == 'movie' else None, tv_show_id=db_media.id if media_type == 'tv' else None).first()
        if rating:
            rating.score = form.score.data * 2  # Convert 5-star rating to 10-point scale
        else:
            rating = Rating(score=form.score.data * 2, user_id=current_user.id, movie_id=db_media.id if media_type == 'movie' else None, tv_show_id=db_media.id if media_type == 'tv' else None, media_type=media_type)
            db.session.add(rating)
        db.session.commit()
        flash('Your rating has been submitted.')
    return redirect(url_for(f'main.{media_type}_detail', **{f'{media_type}_id': media_id}))

@main.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        page = request.args.get('page', 1, type=int)
        search_results = search_multi(query, page=page)
        return render_template('search_results.html', results=search_results['results'], query=query, page=page, total_pages=search_results['total_pages'], form=form)
    return render_template('search_results.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/profile')
@login_required
def profile():
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, ratings=user_ratings)