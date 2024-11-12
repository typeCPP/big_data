from elasticsearch import Elasticsearch, ElasticsearchWarning
from config import (
    ELASTICSEARCH_HOST,
    ELASTICSEARCH_PORT,
    ELASTICSEARCH_SCHEME,
    ELASTICSEARCH_USERNAME,
    ELASTICSEARCH_PASSWORD,
    ELASTICSEARCH_VERIFY_CERTS,
)
import warnings

# Подавление предупреждений Elasticsearch
warnings.filterwarnings('ignore', category=ElasticsearchWarning)

es_config = {
    'hosts': [{
        'host': ELASTICSEARCH_HOST,
        'port': ELASTICSEARCH_PORT,
        'scheme': ELASTICSEARCH_SCHEME,
    }],
    'verify_certs': ELASTICSEARCH_VERIFY_CERTS
}

if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
    es_config['http_auth'] = (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)

try:
    es = Elasticsearch(**es_config)
    # Проверка подключения
    if not es.ping():
        raise ValueError("Не удалось подключиться к Elasticsearch.")
    print("Успешно подключено к Elasticsearch.")
except ElasticsearchWarning as e:
    print(f"Предупреждение Elasticsearch: {e}")
    es = None
except Exception as e:
    print(f"Ошибка при подключении к Elasticsearch: {e}")
    es = None

def create_elasticsearch_index():
    if es is None:
        print("Не подключено к Elasticsearch. Индекс не создан.")
        return
    index_body = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0
        },
        'mappings': {
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'text'},
                'alternative_name': {'type': 'text'},
                'countries': {'type': 'keyword'},
                'genres': {'type': 'keyword'},
                'fees_ru': {'type': 'long'},
                'fees_world': {'type': 'long'},
                'rating_kp': {'type': 'float'},
                'rating_imdb': {'type': 'float'},
                'critics_ru': {'type': 'float'},
                'critics_world': {'type': 'float'},
                'year': {'type': 'integer'},
                'premiere_ru': {'type': 'date', 'format': 'strict_date_optional_time'},
                'premiere_world': {'type': 'date', 'format': 'strict_date_optional_time'},
                'duration': {'type': 'integer'},
                'ratingMpaa': {'type': 'keyword'},
                'ratingAge': {'type': 'integer'},
                'networks': {'type': 'keyword'}
            }
        }
    }
    try:
        if not es.indices.exists(index='movies'):
            es.indices.create(index='movies', body=index_body)
            print("Индекс 'movies' создан в Elasticsearch.")
        else:
            print("Индекс 'movies' уже существует в Elasticsearch.")
    except ElasticsearchWarning as e:
        print(f"Предупреждение при создании индекса: {e}")
    except Exception as e:
        print(f"Ошибка при создании индекса: {e}")

def index_movie_to_elasticsearch(movie):
    if es is None:
        print("Не подключено к Elasticsearch. Фильм не индексирован.")
        return
    movie_dict = {
        'id': movie.id,
        'name': movie.name,
        'alternative_name': movie.alternative_name,
        'countries': movie.countries.split(',') if movie.countries else [],
        'genres': movie.genres.split(',') if movie.genres else [],
        'fees_ru': movie.fees_ru,
        'fees_world': movie.fees_world,
        'rating_kp': movie.rating_kp,
        'rating_imdb': movie.rating_imdb,
        'critics_ru': movie.critics_ru,
        'critics_world': movie.critics_world,
        'year': movie.year,
        'premiere_ru': movie.premiere_ru.isoformat() if movie.premiere_ru else None,
        'premiere_world': movie.premiere_world.isoformat() if movie.premiere_world else None,
        'duration': movie.duration,
        'ratingMpaa': movie.ratingMpaa,
        'ratingAge': movie.ratingAge,
        'networks': movie.networks.split(',') if movie.networks else []
    }
    try:
        es.index(index='movies', id=movie.id, document=movie_dict)
        print(f"Фильм с ID {movie.id} индексирован в Elasticsearch.")
    except ElasticsearchWarning as e:
        print(f"Предупреждение при индексировании фильма ID {movie.id}: {e}")
    except Exception as e:
        print(f"Ошибка при индексировании фильма ID {movie.id}: {e}")
