from flask import Flask
import requests

app = Flask(__name__)

date_server_url = 'http://date-server:5000/date'
converter_url = 'http://timezone-converter:5001/convert'

@app.route('/public-date')
def get_public_date():
    try:
        date_response = requests.get(date_server_url).json()
        converter_response = requests.post(converter_url, json=date_response).json()
        return converter_response
    except Exception as e:
        return {
            "error": str(e)
        }, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)