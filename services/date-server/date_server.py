from flask import Flask
import pytz
from datetime import datetime
app = Flask(__name__)
@app.route('/date', methods=['GET'])
def get_date():
    # Get current time in Tomsk (UTC+5)
    tomsk_tz = pytz.timezone('Asia/Tomsk')
    current_time = datetime.now(tomsk_tz)
    return {
        'date': current_time.isoformat()
    }
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)