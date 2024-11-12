# app/main.py

import sys
import asyncio

from models import create_tables
from elasticsearch_client import create_elasticsearch_index
from downloader import download_movies
from config import API_KEY

def main():
    # Используем API_KEY из config.py или переопределяем через аргументы командной строки
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = API_KEY
        if not api_key:
            print("API-ключ не предоставлен. Установите API_KEY в config.py или передайте его как аргумент.")
            sys.exit(1)

    # Создаем таблицы в базе данных
    create_tables()

    # Создаем индекс в Elasticsearch
    create_elasticsearch_index()

    # Асинхронная загрузка фильмов
    ioloop = asyncio.get_event_loop()
    tasks = []
    # Укажите диапазон страниц для загрузки
    for i in range(1, 5):  # Измените диапазон по необходимости
        tasks.append(download_movies(i, api_key))
    ioloop.run_until_complete(asyncio.gather(*tasks))
    ioloop.close()

if __name__ == "__main__":
    main()
