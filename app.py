import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

admin_key = os.environ.get("ADMIN_KEY")
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
    username = db.Column(db.String(36), primary_key=True, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), unique=True, nullable=False)
    last_request_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'


@app.route('/')
def hello_world():
    return jsonify(message='Hello World'), 200


@app.route('/health-check', methods=['GET'])
def health_check():
    return jsonify(status='OK', message="System Working!"), 200


@app.route('/electric-check', methods=['GET'])
def electric_check():
    username = request.headers.get('username', None)
    if username is None:
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify(message='User not found'), 404

    last_request_date = datetime.now()
    user.last_request_date = last_request_date
    db.session.commit()
    return jsonify(status='OK', message='Last request date updated', data={'user': user.email, 'last_request_date': last_request_date.isoformat()}), 200


@app.route('/users/list', methods=['GET'])
def users_list():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != admin_key:
        return jsonify(status="NOK", message='Operation Failed.'), 400

    users = User.query.all()
    return jsonify(status='OK', message='Users retrieved successfully', data={'users': [{'username': user.username, 'email': user.email, 'last_request_date': user.last_request_date.isoformat() if user.last_request_date else None} for user in users]}), 200


@app.route('/users/register', methods=['POST'])
def create_user():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != admin_key:
        return jsonify(status="NOK", message='Invalid or missing admin key'), 400

    data = request.get_json()
    email = data.get('email')

    if email is None:
        return jsonify(status="NOK", message='Email is required'), 400

    if User.query.filter_by(email=email).first():
        return jsonify(status="NOK", message='Email already registered'), 409

    new_user = User(email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(status='OK', message='User created', data={'user': {'username': new_user.username, 'email': new_user.email}}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
