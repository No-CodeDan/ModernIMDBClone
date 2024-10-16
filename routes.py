from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, Movie, Rating, Cast, Crew
from forms import LoginForm, RegistrationForm, SearchForm, RatingForm
from utils import get_average_rating

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    movies = Movie.query.order_by(Movie.year.desc()).limit(10).all()
    return render_template('index.html', movies=movies)

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
    movies = Movie.query.order_by(Movie.title).paginate(page=page, per_page=20)
    return render_template('movie_list.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    cast = Cast.query.filter_by(movie_id=movie_id).all()
    crew = Crew.query.filter_by(movie_id=movie_id).all()
    avg_rating = get_average_rating(movie)
    form = RatingForm()
    return render_template('movie_detail.html', movie=movie, cast=cast, crew=crew, avg_rating=avg_rating, form=form)

@app.route('/rate/<int:movie_id>', methods=['POST'])
@login_required
def rate_movie(movie_id):
    form = RatingForm()
    if form.validate_on_submit():
        rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
        if rating:
            rating.score = form.score.data
        else:
            rating = Rating(score=form.score.data, user_id=current_user.id, movie_id=movie_id)
            db.session.add(rating)
        db.session.commit()
        flash('Your rating has been submitted.')
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        movies = Movie.query.filter(Movie.title.ilike(f'%{query}%')).all()
        return render_template('search_results.html', movies=movies, query=query)
    return render_template('search_results.html', form=form)

@app.route('/profile')
@login_required
def profile():
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, ratings=user_ratings)
