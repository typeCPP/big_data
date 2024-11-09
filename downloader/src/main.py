import asyncio
import sys
import requests
import json

from models import Movie, create_tables, add_movie_to_db


def try_parse_int(value):
    try:
        return int(value)
    except:
        return None

def try_parse_float(value):
    try:
        return float(value)
    except:
        return None


currency_map = {
    "€": 0.93,
    "$": 1,
}


def currency_to_dollar(value: int, currency: str):
    return value * currency_map[currency]


def parse_fees(value: dict, key: str):
    if key in value.keys():
        if "value" in value[key].keys():
            return currency_to_dollar(value[key]["value"], value[key]["currency"])


def field_or_none(value, field):
    return value[field] if field in value.keys() else None


def parse_premiere(doc, place):
    premiere = field_or_none(doc, "premiere")
    return premiere[place] if premiere else None


def movie_from_json(doc: dict) -> Movie:
    return Movie(
        id=try_parse_int(doc["id"]),
        name=doc["name"],
        alternative_name=doc["alternativeName"],
        genres=', '.join([genre['name'] for genre in doc.get('genres', [])]),
        countries=', '.join([country['name'] for country in doc.get('countries', [])]),
        fees_ru=parse_fees(doc["fees"], "russia") if "fees" in doc.keys() else None,
        fees_world=parse_fees(doc["fees"], "world") if "fees" in doc.keys() else None,
        rating_kp=try_parse_float(doc["rating"]["kp"]),
        rating_imdb=try_parse_float(doc["rating"]["imdb"]),
        critics_ru=try_parse_float(doc["rating"]["russianFilmCritics"]),
        critics_world=try_parse_float(doc["rating"]["filmCritics"]),
        year=try_parse_int(doc["year"]),
        premiere_ru=parse_premiere(doc, "russia"),
        premiere_world=parse_premiere(doc, "world"),
        duration=try_parse_int(field_or_none(doc, "movieLength")),
        ratingMpaa=field_or_none(doc, "ratingMpaa"),
        ratingAge=try_parse_int(field_or_none(doc, "ageRating")),
        networks=""
    )


async def download_movies(page: int):
    print(f"Downloading page {page}")

    headers = {'X-API-KEY': sys.argv[1], 'accept': 'application/json'}
    params = {'page': page, 'limit': 250}
    response = requests.get('https://api.kinopoisk.dev/v1.4/movie', params=params, headers=headers)

    doc = json.loads(response.content.decode('utf-8'))
    for d in doc["docs"]:
        movie = movie_from_json(d)
        if movie:
            add_movie_to_db(movie)


create_tables()

ioloop = asyncio.get_event_loop()
tasks = []

for i in range(58, 60):
    tasks.append(ioloop.create_task(download_movies(i)))

ioloop.run_until_complete(asyncio.wait(tasks))
ioloop.close()
