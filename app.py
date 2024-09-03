import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db_host = os.environ.get("HOST")
db_user = os.environ.get("USER")
db_password = os.environ.get("PASSWORD")
db_database = os.environ.get("DATABASE")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    last_request_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'


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
