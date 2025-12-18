import pytest
from datetime import datetime
import pytz
from date_server.app import app  # Импортируйте ваш Flask app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_date_route_exists(client):
    """Проверяем, что маршрут /date существует"""
    response = client.get('/date')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_date_format_is_iso(client):
    """Проверяем, что дата возвращается в ISO формате"""
    response = client.get('/date')
    data = response.get_json()
    
    # Проверяем наличие ключа 'date'
    assert 'date' in data
    
    # Проверяем, что строка является валидной ISO датой
    try:
        datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"Invalid ISO date format: {data['date']}")

def test_date_is_tomsk_timezone(client):
    """Проверяем, что время соответствует часовому поясу Томска (UTC+7)"""
    response = client.get('/date')
    data = response.get_json()
    
    # Парсим дату
    parsed_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    
    # Проверяем, что часовой пояс правильный
    tomsk_tz = pytz.timezone('Asia/Tomsk')
    # Можно проверить смещение (Томск UTC+7)
    offset = parsed_date.astimezone(tomsk_tz).utcoffset()
    assert offset.total_seconds() == 7 * 3600  # UTC+7 в секундах

def test_response_structure(client):
    """Проверяем структуру JSON ответа"""
    response = client.get('/date')
    data = response.get_json()
    
    # Проверяем структуру
    assert isinstance(data, dict)
    assert len(data) == 1  # Только один ключ 'date'
    assert 'date' in data
    assert isinstance(data['date'], str)