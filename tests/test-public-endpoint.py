import pytest
from unittest.mock import patch, Mock
from public_endpoint.app import app  # Импортируйте ваш Flask app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_public_date_route_exists(client):
    """Проверяем, что маршрут /public-date существует"""
    response = client.get('/public-date')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

@patch('public_endpoint.app.requests.get')
def test_public_endpoint_calls_converter(mock_get, client):
    """Проверяем, что публичный эндпоинт вызывает конвертер"""
    # Мокаем ответ от конвертера
    mock_response = Mock()
    mock_response.json.return_value = {
        'moscow_time': '2024-01-15T06:30:00+03:00'
    }
    mock_get.return_value = mock_response
    
    response = client.get('/public-date')
    
    # Проверяем вызов
    mock_get.assert_called_once_with('http://converter:5001/convert')
    
    # Проверяем ответ
    data = response.get_json()
    assert 'converted_date' in data
    assert data['converted_date'] == '2024-01-15T06:30:00+03:00'

@patch('public_endpoint.app.requests.get')
def test_public_endpoint_returns_only_converted_date(mock_get, client):
    """Проверяем, что возвращается только конвертированная дата"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'original_date': '2024-01-15T10:30:00+07:00',
        'tomsk_time': '2024-01-15T10:30:00+07:00',
        'moscow_time': '2024-01-15T06:30:00+03:00'
    }
    mock_get.return_value = mock_response
    
    response = client.get('/public-date')
    data = response.get_json()
    
    # Проверяем, что только один ключ
    assert len(data) == 1
    assert 'converted_date' in data
    assert 'original_date' not in data
    assert 'tomsk_time' not in data

@patch('public_endpoint.app.requests.get')
def test_error_handling_in_public_endpoint(mock_get, client):
    """Проверяем обработку ошибок в публичном эндпоинте"""
    mock_get.side_effect = Exception("Service unavailable")
    
    response = client.get('/public-date')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data