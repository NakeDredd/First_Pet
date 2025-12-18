import pytest
import sys
import os
from unittest.mock import patch, Mock

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, '../src/timezone-converter'))

from timezone_converter import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('timezone_converter.requests.get')
def test_converter_endpoint(mock_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {'date': '2024-01-20T15:30:00+07:00'}
    mock_get.return_value = mock_response
    
    response = client.get('/convert')
    assert response.status_code == 200
    data = response.get_json()
    assert 'original_date' in data
    assert 'tomsk_time' in data
    assert 'moscow_time' in data