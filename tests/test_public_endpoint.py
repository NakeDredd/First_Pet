import pytest
import sys
import os
from unittest.mock import patch, Mock

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, '../src/public-endpoint'))

from public_endpoint import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('public_endpoint.requests.get')
def test_public_date_endpoint(mock_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {'moscow_time': '2024-01-20T10:30:00+03:00'}
    mock_get.return_value = mock_response
    
    response = client.get('/public-date')
    assert response.status_code == 200
    data = response.get_json()
    assert 'converted_date' in data