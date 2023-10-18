import json
import pytest
from red_alerts import app as flask_app
from red_alerts.shared import redis_client

# Use the app fixture from conftest.py
SAMPLE_DATA = [
    {
        "id": 1,
        "alerts": [
            {
                "time": 1622200800,
                "cities": ["CityA", "CityB"]
            }
        ]
    },
    {
        "id": 2,
        "alerts": [
            {
                "time": 1622287200,
                "cities": ["CityA"]
            }
        ]
    }
]


@pytest.fixture(autouse=True)
def mock_redis_get(monkeypatch):
    def mock_get(key):
        return json.dumps(SAMPLE_DATA)

    monkeypatch.setattr(redis_client, 'get', mock_get)


def test_home_without_filters(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 2  # As we have two records in SAMPLE_DATA


def test_home_with_cities_filter(client):
    response = client.get('/?cities=CityB')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 1  # Only one alert matches 'CityB'


def test_home_with_since_id_filter(client):
    response = client.get('/?since_id=1')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 1  # Only one alert has id > 1


def test_home_with_since_date_filter(client):
    response = client.get('/?since_date=1622250000')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 1  # Only one alert has time > 1622250000


def test_redis_fetch_error(client, monkeypatch):
    """Test error handling when there's an issue fetching data from Redis."""

    # Mock redis_client.get to raise an exception.
    def mock_raise_exception(key):
        raise Exception("Redis fetch failed!")

    monkeypatch.setattr(redis_client, 'get', mock_raise_exception)

    response = client.get('/')
    assert response.status_code == 500
    data = json.loads(response.data.decode('utf-8'))
    assert data["error"] == "Failed to fetch data from Redis"
    assert data["details"] == "Redis fetch failed!"


def test_invalid_since_id_format(client):
    response = client.get('/?since_id=abcd')
    assert response.status_code == 200  # Assuming you handle this as a bad request


def test_empty_city_string(client):
    response = client.get('/?city=')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    # Depending on your logic, check if the response is as expected.


def test_no_data_in_redis(monkeypatch, client):
    def mock_get_none(key):
        return None

    monkeypatch.setattr(redis_client, 'get', mock_get_none)

    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 0  # Expecting empty data
