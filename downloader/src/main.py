import sys
import requests
import json

from models import Movie, create_tables, add_movie_to_db, Person, add_person_to_db
from multiprocessing import Pool


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
    try:
        if not doc:
            return None

        networks = ''
        if 'networks' in doc.keys():
            if doc['networks'] and 'items' in doc['networks']:
                networks = ','.join([network['name'] for network in doc.get('networks', {}).get('items', [])])

        return Movie(
            id=try_parse_int(doc["id"]),
            name=doc["name"],
            alternative_name=doc["alternativeName"],
            genres=','.join([genre['name'] for genre in doc.get('genres', [])]) if 'genres' in doc.keys() else None,
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
            networks=networks,
        )
    except Exception as e:
        raise Exception
        return None


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
        return data['fields']


SELECT_FIELDS = load_select_fields()
FAILED_PAGES = []


def download_movies(page: int):
    global SELECT_FIELDS
    print(f"Downloading page {page}")

    headers = {'X-API-KEY': sys.argv[1], 'accept': 'application/json'}
    params = {'page': page, 'limit': 250, 'selectFields': SELECT_FIELDS}

    response = requests.get('https://api.kinopoisk.dev/v1.4/movie', params=params, headers=headers)
    if response.status_code != 200:
        print('Request for page', page, 'failed', ' Reason: ', response.reason)
        return False, page

    # try:
    doc = json.loads(response.content.decode('utf-8'))
    for d in doc["docs"]:
        movie = movie_from_json(d)
        if movie:
            add_movie_to_db(movie)
            parse_persons(d, movie.id)
    # except Exception as e:
    #     print('Failed parsing page:', page, 'Error:', e)
    #     return False

    return True, page


def parse_page_callback(result):
    is_ok, page = result
    if not is_ok:
        FAILED_PAGES.append(page)


def main():
    create_tables()

    pool = Pool(processes=100)
    for i in range(2820, 2930):
        pool.apply_async(download_movies, args=(i, ), callback=parse_page_callback)
    pool.close()
    pool.join()

    while len(FAILED_PAGES) > 0:
        print('FAILED_PAGES', sorted(FAILED_PAGES))
        pool2 = Pool(processes=100)
        for i in FAILED_PAGES:
            pool2.apply_async(download_movies, args=(i,), callback=parse_page_callback)
        pool2.close()
        pool2.join()


if __name__ == "__main__":
    main()
