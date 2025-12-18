import pytest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, '../src/date-server'))

from date_server import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_date_endpoint_exists(client):
    response = client.get('/date')
    assert response.status_code == 200

def test_date_returns_json(client):
    response = client.get('/date')
    assert response.content_type == 'application/json'

def test_date_has_correct_structure(client):
    response = client.get('/date')
    data = response.get_json()
    assert 'date' in data
    assert isinstance(data['date'], str)