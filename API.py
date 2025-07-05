import os
import requests
from IO import get_cached_data, get_cache_exists, cache_data

def get_api_response(url):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('BB_TMDB_API_KEY')}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_movies(list_id, verbose=False):
    response = get_api_response(f"https://api.themoviedb.org/4/list/{list_id}?language=en-US&page=1")

    movie_list = response['results']

    total_pages = response['total_pages']
    for idx in range(1, total_pages):
        movie_list.extend(get_api_response(f"https://api.themoviedb.org/4/list/{list_id}?language=en-US&page={idx+1}")['results'])

    if verbose:
        print(",\n".join([str(item) for item in movie_list]))
    return movie_list

def get_genres(cached=True, verbose=False):
    if cached and get_cache_exists("genres"):
        return get_cached_data("genres")

    response = get_api_response("https://api.themoviedb.org/3/genre/movie/list?language=en")

    genre_list = response['genres']
    genre_lookup = {genre['id']: genre['name'] for genre in genre_list}

    if verbose:
        print(genre_lookup)

    if cached:
        cache_data(genre_lookup, "genres")

    return genre_lookup