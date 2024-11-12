import os

# Настройки базы данных
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '123143')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('POSTGRES_DB', 'big_data')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Настройки Elasticsearch
ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT', 9200)
ELASTICSEARCH_SCHEME = os.environ.get('ELASTICSEARCH_SCHEME', 'http')
ELASTICSEARCH_USERNAME = os.environ.get('ELASTICSEARCH_USERNAME', None)
ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD', None)
ELASTICSEARCH_VERIFY_CERTS = os.environ.get('ELASTICSEARCH_VERIFY_CERTS', 'False') == 'True'

# Настройки API
API_KEY = os.environ.get('API_KEY', 'your_default_api_key')
API_URL = 'https://api.kinopoisk.dev/v1.4/movie'
