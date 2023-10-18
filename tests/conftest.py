import pytest
from red_alerts import app as flask_app
from red_alerts.shared import redis_client


@pytest.fixture(scope="session")
def app():
    """
    Provides an instance of our Flask app.
    """
    return flask_app


@pytest.fixture
def client(app):
    with app.test_request_context():
        yield app.test_client()


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """
    Auto-used fixture to mock Redis interactions.
    For this mock, all set operations do nothing.
    """
    def mock_set(*args, **kwargs):
        return

    monkeypatch.setattr(redis_client, 'set', mock_set)


@pytest.fixture(autouse=True)
def mock_get(monkeypatch):
    """
    Auto-used fixture to mock Redis get interactions.
    Returns an empty list in JSON format.
    """
    def mock_get(*args, **kwargs):
        return '[]'

    monkeypatch.setattr(redis_client, 'get', mock_get)
