import os
import requests

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def get_popular_movies(page=1):
    url = f'{BASE_URL}/movie/popular'
    params = {
        'api_key': TMDB_API_KEY,
        'page': page
    }
    response = requests.get(url, params=params)
    return response.json()

def search_movies(query, page=1):
    url = f'{BASE_URL}/search/movie'
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
        'append_to_response': 'credits'
    }
    response = requests.get(url, params=params)
    return response.json()
