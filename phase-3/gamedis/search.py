# search
from markupsafe import escape
from flask import render_template, Blueprint, request
from flask_login import current_user
from elasticsearch import Elasticsearch
from decouple import config
import math

ELASTIC_PASSWORD = config('ELASTIC_PASSWORD', "Elasticnotsearch")

es = Elasticsearch("https://localhost:9200",
                   http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

s = Blueprint('search', __name__)


def get_unique_game_genres():

    body = {
        "size": 1000,
        "from": 0,
        "_source": ["Genre"],
        "query": {
            "match_all": {}
        }
    }

    res = es.search(index='gamedis', body=body)
    hits = res['hits']['hits']
    game_genres = set(hit['_source']['Genre']
                      for hit in hits if 'Genre' in hit['_source'])

    return list(game_genres)


def get_unique_creator_names():

    body = {
        "size": 1000,
        "from": 0,
        "_source": ["Creator"],
        "query": {
            "match_all": {}
        }
    }

    res = es.search(index='gamedis', body=body)
    hits = res['hits']['hits']
    creator_names = set(hit['_source']['Creator']
                        for hit in hits if 'Creator' in hit['_source'])

    return list(creator_names)


def get_price_ranges():
    
    max_price_query = {"aggs": {"max_price": {"max": {"field": "Price"}}}} 
    max_price_res = es.search(index='gamedis', body=max_price_query)

    try:
        max_price = max_price_res['aggregations']['max_price']['value']
    except KeyError:
        # Handle the error, e.g., set a default max_price or return an error response
        max_price = 0

    # # Generate price ranges based on the specified ranges
    price_ranges = []

    # # Range below 100 Baht
    price_ranges.append("< 100 Baht")

    # # Range between 100-150 Baht
    price_ranges.append("100-150 Baht")

    # # Intervals of 50 Baht starting from 150 Baht
    current_price = 150
    while current_price <= max_price:
        price_ranges.append(f"{current_price}-{current_price + 50} Baht")
        current_price += 50

    return price_ranges


@s.route('/')
def searchHome():

    game_genres = get_unique_game_genres()
    creator_names = get_unique_creator_names()
    price_ranges = get_price_ranges()

    return render_template('search.html', user=current_user, game_genres=game_genres, creator_names=creator_names, price_ranges=price_ranges)


@s.route('/search')
def search():

    game_genres = get_unique_game_genres()
    creator_names = get_unique_creator_names()
    price_ranges = get_price_ranges()

    page_size = 7
    keyword = request.args.get('keyword')
    page_no = int(request.args.get('page', 1))
    genre = request.args.get('genre')
    price_range = request.args.get('price_range')
    creator = request.args.get('creator')

    lowercase_keyword = keyword.lower()
    regex_pattern = '.*' + '.*?'.join(['[{}{}]'.format(
        letter.lower(), letter.upper()) for letter in lowercase_keyword]) + '.*'

    body = {
        'size': page_size,
        'from': page_size * (page_no - 1),

        "query": {
            "bool": {
                "should": [
                    {"regexp": {"Name": regex_pattern}}
                ],
                "must": []
            }
        }

    }

    if genre:

        lowercase_genre = genre.lower()
        regex_pattern_genre = '.*' + '.*?'.join(['[{}{}]'.format(
            letter.lower(), letter.upper()) for letter in lowercase_genre]) + '.*'

        body['query']['bool']['must'].append(
            {"regexp": {"Genre": regex_pattern_genre}})

    elif creator:

        lowercase_creator = creator.lower()
        regex_pattern_creator = '.*' + '.*?'.join(['[{}{}]'.format(
            letter.lower(), letter.upper()) for letter in lowercase_creator]) + '.*'

        body['query']['bool']['must'].append(
            {"regexp": {"Creator": regex_pattern_creator}})

    elif price_range:

        if price_range == "< 100 Baht":
            min_price = 0
            max_price = 100
        elif price_range == "100-150 Baht":
            min_price = 100
            max_price = 150
        else:
            min_price, max_price = map(
                int, price_range.replace(" Baht", "").split("-"))

        body['query']['bool']['must'].append({
            "range": {
                "Price": {
                    "gte": min_price,
                    "lte": max_price
                }
            }
        })

    res = es.search(index='gamedis', body=body)

    hits = [
        {
            'Image': doc['_source']['Picture'],
            'Name': doc['_source']['Name'],
            'Creator': doc['_source']['Creator'],
            'Genre': doc['_source']['Genre'],
            'Price': doc['_source']['Price'],
            'Review': doc['_source']['Review'],
            'Review from User': doc['_source']['Review from User']
        }
        for doc in res['hits']['hits']
    ]

    page_total = math.ceil(res['hits']['total']['value'] / page_size)

    return render_template('search.html', keyword=keyword, results=hits, page_no=page_no, totalPages=page_total, user=current_user, game_genres=game_genres, creator_names=creator_names, price_ranges=price_ranges)
