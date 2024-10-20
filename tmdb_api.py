import os
import requests
from datetime import datetime, timedelta

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def get_popular_movies(page=1, genre_id=None):
    url = f'{BASE_URL}/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'page': page,
        'sort_by': 'popularity.desc'
    }
    if genre_id:
        params['with_genres'] = genre_id
    response = requests.get(url, params=params)
    return response.json()

def get_popular_tv_shows(page=1, genre_id=None, region='US', days_ago=30):
    url = f'{BASE_URL}/discover/tv'
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    params = {
        'api_key': TMDB_API_KEY,
        'page': page,
        'sort_by': 'popularity.desc',
        'with_origin_country': region,
        'first_air_date.gte': start_date,
        'first_air_date.lte': end_date
    }
    if genre_id:
        params['with_genres'] = genre_id
    response = requests.get(url, params=params)
    return response.json()

def search_multi(query, page=1):
    url = f'{BASE_URL}/search/multi'
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'page': page
    }
    response = requests.get(url, params=params)
    return response.json()

def get_movie_details(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'append_to_response': 'credits,watch/providers'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_tv_show_details(tv_id):
    url = f'{BASE_URL}/tv/{tv_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'append_to_response': 'credits,watch/providers'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_genres(media_type='movie'):
    url = f'{BASE_URL}/genre/{media_type}/list'
    params = {
        'api_key': TMDB_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()['genres']

def get_similar_tv_shows(tv_id, page=1):
    url = f'{BASE_URL}/tv/{tv_id}/similar'
    params = {
        'api_key': TMDB_API_KEY,
        'page': page
    }
    response = requests.get(url, params=params)
    return response.json()
