from flask import Flask
import requests
app = Flask(__name__)
@app.route('/public-date', methods=['GET'])
def get_public_date():
    try:
        # Fetch the converted date from the timezone converter
        response = requests.get('http://converter:5001/convert')
        data = response.json()
        
        return {
            'original_date': data['original_date'],
            'tomsk_time': data['tomsk_time'],
            'moscow_time': data['moscow_time']
        }
    except Exception as e:
        return {'error': str(e)}, 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)