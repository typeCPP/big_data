# app/parsers.py

from datetime import datetime
from models import Movie, Person

def try_parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def try_parse_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def try_parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except (ValueError, TypeError):
        return None

def currency_to_dollar(value: int, currency: str):
    currency_map = {
        "€": 0.93,
        "$": 1,
    }
    return value * currency_map.get(currency, 1)

def parse_fees(value: dict, key: str):
    if key in value.keys():
        fee_info = value[key]
        if "value" in fee_info and "currency" in fee_info:
            return currency_to_dollar(fee_info["value"], fee_info["currency"])
    return None

def field_or_none(value, field):
    return value.get(field, None)

def parse_premiere(doc, place):
    premiere = field_or_none(doc, "premiere")
    if premiere and place in premiere:
        return try_parse_date(premiere[place])
    return None

def movie_from_json(doc: dict) -> Movie:
    genres_list = [genre['name'] for genre in doc.get('genres', []) if 'name' in genre]
    countries_list = [country['name'] for country in doc.get('countries', []) if 'name' in country]
    networks_list = [network['name'] for network in doc.get('networks', {}).get('items', []) if 'name' in network]

    return Movie(
        id=try_parse_int(doc.get("id")),
        name=doc.get("name"),
        alternative_name=doc.get("alternativeName"),
        genres=','.join(genres_list),
        countries=','.join(countries_list),
        fees_ru=parse_fees(doc.get("fees", {}), "russia"),
        fees_world=parse_fees(doc.get("fees", {}), "world"),
        rating_kp=try_parse_float(doc.get("rating", {}).get("kp")),
        rating_imdb=try_parse_float(doc.get("rating", {}).get("imdb")),
        critics_ru=try_parse_float(doc.get("rating", {}).get("russianFilmCritics")),
        critics_world=try_parse_float(doc.get("rating", {}).get("filmCritics")),
        year=try_parse_int(doc.get("year")),
        premiere_ru=parse_premiere(doc, "russia"),
        premiere_world=parse_premiere(doc, "world"),
        duration=try_parse_int(field_or_none(doc, "movieLength")),
        ratingMpaa=field_or_none(doc, "ratingMpaa"),
        ratingAge=try_parse_int(field_or_none(doc, "ageRating")),
        networks=','.join(networks_list)
    )

def person_from_json(doc: dict, movie_id: int) -> Person:
    return Person(
        id=try_parse_int(doc.get("id")),
        movie_id=movie_id,
        name=doc.get('name', None),
        en_name=doc.get('enName', None),
        profession=doc.get('profession', None),
        en_profession=doc.get('enProfession', None)
    )

def parse_persons(movie_json: dict, movie_id: int):
    persons = []
    if "persons" in movie_json.keys():
        for p in movie_json["persons"]:
            person = person_from_json(p, movie_id)
            if person:
                persons.append(person)
    return persons
