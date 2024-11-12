# app/downloader.py

import requests
import json

from parsers import movie_from_json, parse_persons
from database import get_session
from elasticsearch_client import index_movie_to_elasticsearch
from config import API_URL
from sqlalchemy.exc import IntegrityError

def load_select_fields():
    try:
        with open('select_fields.json') as json_data:
            data = json.load(json_data)
            print(f"Загружены поля: {data['fields']}")
            return data['fields']
    except Exception as e:
        print(f"Ошибка при загрузке 'select_fields.json': {e}")
        return []

async def download_movies(page: int, api_key: str):
    print(f"Загрузка страницы {page}...")

    headers = {
        'X-API-KEY': api_key,
        'accept': 'application/json'
    }
    select_fields = load_select_fields()
    params = {
        'page': page,
        'limit': 250,
        'selectFields': select_fields
    }

    print("Отправка запроса с параметрами:")
    print("Headers:", headers)
    print("Params:", params)
    print("URL:", API_URL)

    try:
        response = requests.get(API_URL, params=params, headers=headers)
        print("URL запроса:", response.url)  # Печать полной URL
        response.raise_for_status()  # Вызывает ошибку, если статус ответа не 2xx
    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы {page}: {e}")
        if response is not None:
            print("Текст ошибки от API:", response.text)  # Печать текста ответа от API
        return

    try:
        doc = response.json()
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON на странице {page}: {e}")
        return

    session = get_session()

    for d in doc.get("docs", []):
        movie = movie_from_json(d)
        if movie:
            try:
                session.add(movie)
                session.commit()
                print(f"Фильм '{movie.name}' добавлен в базу данных.")
                # Индексируем фильм в Elasticsearch
                index_movie_to_elasticsearch(movie)
            except IntegrityError:
                session.rollback()
                print(f"Фильм с ID {movie.id} уже существует в базе данных.")
            except Exception as e:
                session.rollback()
                print(f"Ошибка при добавлении фильма ID {movie.id}: {e}")
            # Парсим и добавляем персон
            try:
                persons = parse_persons(d, movie.id)
                for person in persons:
                    try:
                        session.add(person)
                        session.commit()
                    except IntegrityError:
                        session.rollback()
                        print(f"Персона с ID {person.id} уже существует в базе данных.")
                    except Exception as e:
                        session.rollback()
                        print(f"Ошибка при добавлении персоны ID {person.id}: {e}")
                if persons:
                    print(f"Добавлено {len(persons)} персон для фильма ID {movie.id}.")
            except Exception as e:
                print(f"Ошибка при парсинге персон для фильма ID {movie.id}: {e}")

    session.close()
