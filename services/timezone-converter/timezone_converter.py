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