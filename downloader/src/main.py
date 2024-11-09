import asyncio
import sys
import requests
import json

from models import Movie, create_tables, add_movie_to_db, Person, add_person_to_db


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


def parse_premiere(doc, place):
    premiere = doc.get('premiere', None)
    return premiere[place] if premiere else None


def movie_from_json(doc: dict) -> Movie:
    return Movie(
        id=try_parse_int(doc["id"]),
        name=doc["name"],
        alternative_name=doc["alternativeName"],
        genres=','.join([genre['name'] for genre in doc.get('genres', [])]),
        countries=','.join([country['name'] for country in doc.get('countries', [])]),
        fees_ru=parse_fees(doc["fees"], "russia") if "fees" in doc.keys() else None,
        fees_world=parse_fees(doc["fees"], "world") if "fees" in doc.keys() else None,
        rating_kp=try_parse_float(doc["rating"]["kp"]),
        rating_imdb=try_parse_float(doc["rating"]["imdb"]),
        critics_ru=try_parse_float(doc["rating"]["russianFilmCritics"]),
        critics_world=try_parse_float(doc["rating"]["filmCritics"]),
        year=try_parse_int(doc["year"]),
        premiere_ru=parse_premiere(doc, "russia"),
        premiere_world=parse_premiere(doc, "world"),
        duration=try_parse_int(doc.get('movieLength', None)),
        ratingMpaa=doc.get('ratingMpaa', None),
        ratingAge=try_parse_int(doc.get('ageRating', None)),
        networks=','.join([network['name'] for network in doc.get('networks', dict()).get('items', [])]),
    )


def person_from_json(doc: dict, movie_id: int) -> Person:
    return Person(
        id=doc["id"],
        movie_id=movie_id,
        name=doc.get('name', None),
        en_name=doc.get('enName', None),
        profession=doc.get('profession', None),
        en_profession=doc.get('enProfession', None)
    )


def parse_persons(movie_json: dict, movie_id):
    if "persons" in movie_json.keys():
        for p in movie_json["persons"]:
            person = person_from_json(p, movie_id)
            add_person_to_db(person)


def load_select_fields():
    with open('select_fields.json') as json_data:
        data = json.load(json_data)
        print(data['fields'])
        return data['fields']


async def download_movies(page: int):
    print(f"Downloading page {page}")

    headers = {'X-API-KEY': sys.argv[1], 'accept': 'application/json'}
    params = {'page': page, 'limit': 250, 'selectFields': load_select_fields()}

    response = requests.get('https://api.kinopoisk.dev/v1.4/movie', params=params, headers=headers)

    doc = json.loads(response.content.decode('utf-8'))
    for d in doc["docs"]:
        movie = movie_from_json(d)
        if movie:
            add_movie_to_db(movie)
            parse_persons(d, movie.id)


def main():
    create_tables()

    ioloop = asyncio.get_event_loop()
    tasks = []

    for i in range(58, 60):
        tasks.append(ioloop.create_task(download_movies(i)))

    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()


if __name__ == "__main__":
    main()
