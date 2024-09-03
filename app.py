import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

admin_key = os.environ.get("ADMIN_KEY")
db_host = os.environ.get("HOST")
db_user = os.environ.get("USER")
db_password = os.environ.get("PASSWORD")
db_database = os.environ.get("DATABASE")

DEFAULT_ENDPOINT = 'apispec_1'
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": DEFAULT_ENDPOINT,
            "route": '/{}.json'.format(DEFAULT_ENDPOINT),
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/swagger/"
}

app = Flask(__name__)
swagger = Swagger(app, config=swagger_config)

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
@swag_from({
    'responses': {
        200: {
            'description': 'Welcome message',
            'examples': {
                'application/json': {
                    "message": "Hello World"
                }
            }
        }
    }
})
def hello_world():
    return jsonify(message='Hello World'), 200


@app.route('/health-check', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'System working status',
            'examples': {
                'application/json': {
                    "status": "OK",
                    "message": "System Working!"
                }
            }
        }
    }
})
def health_check():
    return jsonify(status='OK', message="System Working!"), 200


@app.route('/electric-check', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'The username of the user.',
                    }
                },
                'required': ['username']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Last request date updated',
            'examples': {
                'application/json': {
                    "status": "OK",
                    "message": "Last request date updated",
                    "data": {
                        "user": "example@mail.com",
                        "last_request_date": "2024-09-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            'description': 'Username is required'
        },
        404: {
            'description': 'User not found'
        }
    }
})
def post_electric_check():
    data = request.get_json()
    username = data.get('username', None)
    if username is None:
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify(message='User not found'), 404

    last_request_date = datetime.now()
    user.last_request_date = last_request_date
    db.session.commit()
    return jsonify(status='OK', message='Last request date updated', data={'user': user.email, 'last_request_date': last_request_date.isoformat()}), 200


@app.route('/electric-check', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'username',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The username of the user.'
        }
    ],
    'responses': {
        200: {
            'description': 'Last request date retrieved',
            'examples': {
                'application/json': {
                    "status": "OK",
                    "message": "Last request date retrieved",
                    "data": {
                        "user": "example@mail.com",
                        "last_request_date": "2024-09-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            'description': 'Username is required'
        },
        404: {
            'description': 'User not found'
        }
    }
})
def get_electric_check():
    username = request.args.get('username', None)
    if username is None:
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify(message='User not found'), 404

    return jsonify(status='OK', message='Last request date retrieved', data={'user': user.email, 'last_request_date': user.last_request_date.isoformat() if user.last_request_date else None}), 200


@app.route('/users/list', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'admin-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'The admin key to authenticate the request.'
        }
    ],
    'responses': {
        200: {
            'description': 'A list of users',
            'examples': {
                'application/json': {
                    "status": "OK",
                    "message": "Users retrieved successfully",
                    "data": {
                        "users": [
                            {
                                "username": "user1-uuid",
                                "email": "user1@mail.com",
                                "last_request_date": "2024-09-01T12:00:00Z"
                            },
                            {
                                "username": "user2-uuid",
                                "email": "user2@mail.com",
                                "last_request_date": "2024-09-01T12:00:00Z"
                            }
                        ]
                    }
                }
            }
        },
        400: {
            'description': 'Invalid or missing admin key'
        }
    }
})
def users_list():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != admin_key:
        return jsonify(status="NOK", message='Operation Failed.'), 400

    users = User.query.all()
    return jsonify(status='OK', message='Users retrieved successfully', data={'users': [{'username': user.username, 'email': user.email, 'last_request_date': user.last_request_date.isoformat() if user.last_request_date else None} for user in users]}), 200


@app.route('/users/register', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'admin-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'The admin key to authenticate the request.'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'description': 'The email of the new user.',
                    }
                },
                'required': ['email']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User created',
            'examples': {
                'application/json': {
                    "status": "OK",
                    "message": "User created",
                    "data": {
                        "user": {
                            "username": "new-user-uuid",
                            "email": "newuser@mail.com"
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Invalid or missing admin key or email is required'
        },
        409: {
            'description': 'Email already registered'
        }
    }
})
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
