
from datetime import datetime

from flask import Flask

app = Flask(__name__)

last_request_date = None


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/health-check', methods=['GET'])
def health_check():
    global last_request_date
    return {'status': 'OK', 'last_request_date': last_request_date}


@app.route('/electric-check', methods=['GET'])
def electric_check():
    global last_request_date
    last_request_date = datetime.now()
    return {'status': 'OK', 'message': 'last request date updated', 'last_request_date': last_request_date}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
