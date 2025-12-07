# Microservices Implementation

## 1. Date Server (date_server.py)
```python
from flask import Flask
import datetime

app = Flask(__name__)

@app.route('/date')
def get_date():
    return {
        "date": datetime.datetime.now().isoformat()
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 2. Timezone Converter (timezone_converter.py)
```python
from flask import Flask, request
import pytz
from datetime import datetime

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_time():
    data = request.json
    try:
        tomsk_time = datetime.fromisoformat(data['date']).replace(tzinfo=pytz.timezone('Asia/Tomsk'))
        moscow_time = tomsk_time.astimezone(pytz.timezone('Europe/Moscow'))
        return {
            "converted_date": moscow_time.isoformat()
        }
    except Exception as e:
        return {
            "error": str(e)
        }, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

## 3. Public Endpoint (public_endpoint.py)
```python
from flask import Flask
import requests

app = Flask(__name__)

date_server_url = 'http://localhost:5000/date'
converter_url = 'http://localhost:5001/convert'

@app.route('/public-date')
def get_public_date():
    try:
        # Get date from first service
        date_response = requests.get(date_server_url).json()
        
        # Convert to Moscow time
        converter_response = requests.post(converter_url, json=date_response).json()
        
        return converter_response
    except Exception as e:
        return {
            "error": str(e)
        }, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
```

## Docker Setup

### Dockerfiles

**date_server/Dockerfile**
```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY date_server.py .
CMD ["python", "date_server.py"]
```

**timezone_converter/Dockerfile**
```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY timezone_converter.py .
CMD ["python", "timezone_converter.py"]
```

**public_endpoint/Dockerfile**
```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY public_endpoint.py .
CMD ["python", "public_endpoint.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  date-server:
    build: ./date_server
    ports:
      - "5000:5000"
    networks:
      microservices-network:
        aliases:
          - date-server

  timezone-converter:
    build: ./timezone_converter
    ports:
      - "5001:5001"
    networks:
      microservices-network:
        aliases:
          - converter

  public-endpoint:
    build: ./public_endpoint
    ports:
      - "5002:5002"
    depends_on:
      - date-server
      - timezone-converter
    networks:
      microservices-network:
        aliases:
          - public-endpoint

networks:
  microservices-network:
    driver: bridge
```

## Requirements File (requirements.txt)
```
pytz
flask
```