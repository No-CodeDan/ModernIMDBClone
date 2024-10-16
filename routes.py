from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, Movie, Rating
from forms import LoginForm, RegistrationForm, SearchForm, RatingForm
from tmdb_api import get_popular_movies, search_movies, get_movie_details
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    popular_movies = get_popular_movies()['results'][:10]
    return render_template('index.html', movies=popular_movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/movies')
def movie_list():
    page = request.args.get('page', 1, type=int)
    popular_movies = get_popular_movies(page=page)
    return render_template('movie_list.html', movies=popular_movies['results'], page=page, total_pages=popular_movies['total_pages'])

@app.route('/movie/<int:movie_id>')
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

@app.route('/rate/<int:movie_id>', methods=['POST'])
@login_required
def rate_movie(movie_id):
    form = RatingForm()
    if form.validate_on_submit():
        db_movie = Movie.query.filter_by(tmdb_id=movie_id).first()
        if not db_movie:
            flash('Movie not found.')
            return redirect(url_for('movie_detail', movie_id=movie_id))
        
        rating = Rating.query.filter_by(user_id=current_user.id, movie_id=db_movie.id).first()
        if rating:
            rating.score = form.score.data
        else:
            rating = Rating(score=form.score.data, user_id=current_user.id, movie_id=db_movie.id)
            db.session.add(rating)
        db.session.commit()
        flash('Your rating has been submitted.')
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        page = request.args.get('page', 1, type=int)
        search_results = search_movies(query, page=page)
        return render_template('search_results.html', movies=search_results['results'], query=query, page=page, total_pages=search_results['total_pages'], form=form)
    return render_template('search_results.html', form=form)

@app.route('/profile')
@login_required
def profile():
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, ratings=user_ratings)
