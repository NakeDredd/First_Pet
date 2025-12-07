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