from flask import Flask
import requests
import pytz
from datetime import datetime
app = Flask(__name__)
@app.route('/convert', methods=['GET'])
def convert_time():
    try:
        # Fetch the current date from the date server (Tomsk time)
        date_response = requests.get('http://date-server:5000/date')
        date_data = date_response.json()
        
        # Parse the date string and convert to Tomsk time (UTC+5)
        tomsk_date = datetime.fromisoformat(date_data['date']).replace(tzinfo=pytz.timezone('Asia/Tomsk'))
        
        # Convert to Moscow time (UTC+3)
        moscow_date = tomsk_date.astimezone(pytz.timezone('Europe/Moscow'))
        
        return {
            'original_date': date_data['date'],
            'tomsk_time': tomsk_date.isoformat(),
            'moscow_time': moscow_date.isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 400
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)