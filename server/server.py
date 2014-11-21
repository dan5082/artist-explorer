from flask import Flask, jsonify, request

from functools import  wraps
from flask_cors import CORS, cross_origin

from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

import pyen

app = Flask(__name__)

#Allowed origins
ORIGINS = ['*']

app.config['CORS_HEADERS'] = "Content-Type"
app.config['CORS_RESOURCES'] = {r"/*": {"origins": ORIGINS}}

cors = CORS(app)

en = pyen.Pyen()

def cached(timeout=5 * 60, key='view/%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator


@app.route('/api/artist-info/<artist_uri>')
@cached(timeout=30 * 60)
def get_artist_info(artist_uri):
    response = en.get('artist/profile', id=artist_uri, bucket=['genre','biographies'])
    return jsonify(response)

@app.route('/api/genres/<genre_name>/artists')
@cached(timeout=30 * 60)
def get_genre_artists(genre_name):
    response = en.get('genre/artists', name=genre_name, results=15, bucket=['id:spotify'], limit=True)
    return jsonify(response)

@app.route('/api/genres')
@cross_origin(origins=ORIGINS)
@cached(timeout=30 * 60)
def get_all_genres():
    response = en.get('genre/list')
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
