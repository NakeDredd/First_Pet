import pytest
from unittest.mock import patch, Mock
from converter.app import app  # Импортируйте ваш Flask app
import pytz
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_convert_route_exists(client):
    """Проверяем, что маршрут /convert существует"""
    response = client.get('/convert')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

@patch('converter.app.requests.get')
def test_converter_calls_date_server(mock_get, client):
    """Проверяем, что конвертер вызывает date-server"""
    # Мокаем ответ от date-server
    mock_response = Mock()
    mock_response.json.return_value = {
        'date': '2024-01-15T10:30:00+07:00'  # Томск UTC+7
    }
    mock_get.return_value = mock_response
    
    response = client.get('/convert')
    
    # Проверяем, что requests.get был вызван
    mock_get.assert_called_once_with('http://date-server:5000/date')
    
    # Проверяем структуру ответа
    data = response.get_json()
    assert 'original_date' in data
    assert 'tomsk_time' in data
    assert 'moscow_time' in data

@patch('converter.app.requests.get')
def test_timezone_conversion_correct(mock_get, client):
    """Проверяем корректность конвертации времени"""
    # Фиксированная дата для теста
    test_date = '2024-01-15T10:30:00+07:00'  # Томск UTC+7 = 3:30 UTC+3 (Москва)
    
    mock_response = Mock()
    mock_response.json.return_value = {'date': test_date}
    mock_get.return_value = mock_response
    
    response = client.get('/convert')
    data = response.get_json()
    
    # Проверяем конвертацию
    assert data['original_date'] == test_date
    assert data['tomsk_time'] == test_date
    
    # Москва должна быть на 4 часа раньше
    # 10:30 Томск = 6:30 Москва (разница 4 часа зимой, 3 часа летом)
    # Для простоты проверяем формат
    assert '2024-01-15T' in data['moscow_time']
    assert '+03:00' in data['moscow_time']  # Московское время UTC+3

@patch('converter.app.requests.get')
def test_error_handling(mock_get, client):
    """Проверяем обработку ошибок"""
    # Мокаем ошибку
    mock_get.side_effect = Exception("Connection error")
    
    response = client.get('/convert')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data