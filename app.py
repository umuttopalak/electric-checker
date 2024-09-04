import uuid
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from flask_mail import Mail, Message
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

swagger = Swagger(app, config=Config.SWAGGER_CONFIG)
mail = Mail(app)

scheduler = BackgroundScheduler()
scheduler.start()


class User(db.Model):
    username = db.Column(db.String(36), primary_key=True, unique=True,
                         nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), unique=True, nullable=False)
    last_request_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'


def send_mail(subject, recipient, body):
    print(recipient)
    msg = Message(
        subject=subject,
        sender=str(app.config.get("MAIL_DEFAULT_SENDER")),
        recipients=[recipient],
        body=body
    )
    mail.send(msg)


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

    user = User.query.filter_by(username=username).first()
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

    user = User.query.filter_by(username=username).first()
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
    return jsonify(status='OK', message='Users retrieved successfully', data={'users': [{'username': user.username, 'email': user.email, 'last_request_date': user.last_request_date.isoformat() if user.last_request_date else None} for user in users]}), 200


@app.route('/admin/users/register', methods=['POST'])
@swag_from('swagger_specs/users_register.yaml')
def create_user():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
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


@app.route('/admin/send-test-email')
def send_test_email():
    send_mail("Deneme", "umuttopalak@hotmail.com", "zort")
    return "Email sent successfully!"


def send_email_to_unreachable_user():
    with app.app_context():
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        inactive_users = User.query.filter(
            User.last_request_date < one_minute_ago).all()
        print(f"inactive users -> {inactive_users}")
        if inactive_users:
            for user in inactive_users:
                send_mail(subject="Dikkat!", recipient=user.email,
                          body=f"Sayın kullanıcımız bir süredir elektriğinize ulaşamıyoruz.")

            print(f"Mail(s) sended to : f{inactive_users}")


scheduler.add_job(func=send_email_to_unreachable_user,
                  trigger="interval", hours=12)

if __name__ == '__main__':
    with app.app_context():
        upgrade()

    app.run(host='0.0.0.0', port=3000)
