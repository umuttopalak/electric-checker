import asyncio
import uuid
from datetime import datetime, timedelta

import telegram
from apscheduler.schedulers.background import BackgroundScheduler
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from flask_mail import Mail, Message
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

swagger = Swagger(app, config=Config.SWAGGER_CONFIG)
mail = Mail(app)

# scheduler = BackgroundScheduler()
# scheduler.start()

bot = telegram.Bot(token=Config.TELEGRAM_TOKEN)


class User(db.Model):
    username = db.Column(db.String(36), primary_key=True, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), unique=True, nullable=False)
    last_request_date = db.Column(db.DateTime, nullable=True)
    has_license = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    chat_id = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "last_request_date": None if self.last_request_date is None else self.last_request_date.isoformat(),
            "has_license": True if self.has_license else False,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "chat_id": self.chat_id,
        }


async def send_information(subject, recipient, body, chat_id):
    try:
        # mail
        msg = Message(
            subject=subject,
            sender=str(app.config.get("MAIL_DEFAULT_SENDER")),
            recipients=[recipient],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        print(f"Error while sending mail to : {recipient}")
    # telegram message
    try:
        message = await bot.send_message(chat_id=chat_id, text=body)
    except Exception as e:
        print(f"Error while sending telegram message to : {recipient}")


@app.route('/')
@swag_from('swagger_specs/hello_world.yaml')
def hello_world():
    return jsonify(message='Hello World'), 200


@app.route('/health-check', methods=['GET'])
@swag_from('swagger_specs/health_check.yaml')
def health_check():
    return jsonify(status='OK', message="System Working!"), 200


@app.route('/user/electric-check', methods=['POST'])
@swag_from('swagger_specs/electric_check_post.yaml')
def post_electric_check():
    data = request.get_json()
    username = data.get('username', None)
    if username is None:
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username, has_license=True).first()
    if user is None:
        return jsonify(message='User not found'), 404

    last_request_date = datetime.now()
    user.last_request_date = last_request_date
    db.session.commit()
    return jsonify(status='OK', message='Last request date updated', data={'user': user.email, 'last_request_date': last_request_date.isoformat()}), 200


@app.route('/user/electric-check', methods=['GET'])
@swag_from('swagger_specs/electric_check_get.yaml')
def get_electric_check():
    username = request.args.get('username', None)
    if username is None:
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username, has_license=True).first()
    if user is None:
        return jsonify(message='User not found'), 404

    return jsonify(status='OK', message='Last request date retrieved', data={'user': user.email, 'last_request_date': user.last_request_date.isoformat() if user.last_request_date else None}), 200


@app.route('/admin/users/list', methods=['GET'])
@swag_from('swagger_specs/users_list.yaml')
def users_list():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        return jsonify(status="NOK", message='Operation Failed.'), 400

    users = User.query.all()
    if users:
        return jsonify(status='OK', message='Users retrieved successfully', data={'users': [user.to_dict() for user in users]}), 200
    return jsonify(status='OK', message='Users retrieved successfully', data={'users': []}), 200


@app.route('/admin/users/register', methods=['POST'])
@swag_from('swagger_specs/users_register.yaml')
def create_user():
    """This endpoint registers a new user."""
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        return jsonify(status="NOK", message='Invalid or missing admin key'), 400

    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')

    if not all([first_name, last_name, email, phone_number]):
        return jsonify(status="NOK", message="Missing information"), 400

    if User.query.filter_by(email=email).first():
        return jsonify(status="NOK", message='Email already registered'), 409

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        chat_id="default"
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(status="OK", message="User created", data={'user': {'username': new_user.username, 'email': new_user.email}}), 201


@app.route('/admin/users/delete/', methods=['DELETE'])
@swag_from('swagger_specs/users_delete.yaml')
def delete_user():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        return jsonify(status="NOK", message='Invalid or missing admin key'), 400

    data = request.get_json()
    email = data.get('email', None)
    if email is None:
        return jsonify(status="NOK", message='Email is Required.'), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="NOK", message='User not found'), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify(status="OK", message='User deleted successfully'), 200


@app.route('/admin/license/deactivate/<username>', methods=['PATCH'])
@swag_from('swagger_specs/license_deactivate.yaml')
def deactivate_license(username):
    """This endpoint allows an admin to deactivate a user's license."""
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify(status="NOK", message="User not found"), 404

    user.has_license = False
    db.session.commit()

    return jsonify(status="OK", message="License deactivated"), 200


@app.route('/admin/license/activate/<username>', methods=['PATCH'])
@swag_from('swagger_specs/license_activate.yaml')
def activate_license(username):
    """This endpoint allows an admin to activate a user's license."""
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify(status="NOK", message="User not found"), 404

    user.has_license = True
    db.session.commit()

    return jsonify(status="OK", message="License activated"), 200


@app.route('/admin/send-test-email')
@swag_from('swagger_specs/send_test_email.yaml')
def send_test_email():
    # Default admin user will be added
    # send_information()
    return "Email sent successfully!"


@app.route('/admin/periodic-check')
@swag_from('swagger_specs/periodic_check.yaml')
def periodic_check():
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400
    
    one_minute_ago = datetime.now() - timedelta(minutes=1)
    inactive_users = User.query.filter(User.last_request_date < one_minute_ago).all()
    print(f"inactive users -> {inactive_users}")
    
    if inactive_users:
        for user in inactive_users:
            print(user)
            asyncio.run(send_information(
                subject="Dikkat!",
                recipient=user.email,
                chat_id=user.chat_id,
                body=f"Sayın kullanıcımız bir süredir elektriğinize ulaşamıyoruz."
            ))

        print(f"Mail(s) sent to: {inactive_users}")

    return "Periodic Check Started!"

@app.route('/telegram/user-data', methods=['POST'])
@swag_from('swagger_specs/user_data_post.yaml')
def create_user_with_telegram():
    """This endpoint receives user information sent by the bot."""
    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    chat_id = data.get('chat_id')

    if not all([first_name, last_name, email, phone_number, chat_id]):
        return jsonify(status="NOK", message="Missing information"), 400

    user = User.query.filter(
        or_(
            User.chat_id == chat_id,
            User.phone_number == phone_number,
            User.email == email)).first()

    if user:
        return jsonify(status="OK", message="User already registered"), 409

    try:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            chat_id=chat_id
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify(status="OK", message="User successfully created"), 201
    except Exception as e:
        return jsonify(status="NOK", message="Operation Failed.", error=f"{str(e)}"), 500


async def send_email_to_unreachable_user():
    with app.app_context():
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        inactive_users = User.query.filter(
            User.last_request_date < one_minute_ago).all()
        print(f"inactive users -> {inactive_users}")
        if inactive_users:
            for user in inactive_users:
                await send_information(subject="Dikkat!",
                                       recipient=user.email,
                                       chat_id='5496812621',
                                       body=f"Sayın kullanıcımız bir süredir elektriğinize ulaşamıyoruz.")

            print(f"Mail(s) sended to : f{inactive_users}")


def run_async_task():
    asyncio.run(send_email_to_unreachable_user())


# scheduler.add_job(func=run_async_task, trigger="interval", seconds=20000)

if __name__ == '__main__':
    with app.app_context():
        upgrade()

    app.run(host='0.0.0.0', port=3000)
