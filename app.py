import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum as PyEnum

import psutil
import telegram
from apscheduler.schedulers.background import BackgroundScheduler
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from flask_mail import Mail, Message
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, or_, text

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

swagger = Swagger(app, config=Config.SWAGGER_CONFIG)
mail = Mail(app)

# logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# scheduler = BackgroundScheduler()
# scheduler.start()

bot = telegram.Bot(token=Config.TELEGRAM_TOKEN)


class User(db.Model):
    username = db.Column(db.String(36), primary_key=True, unique=True,
                         nullable=False, default=lambda: str(uuid.uuid4()))
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


class LogTypeEnum(PyEnum):
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    SYSTEM_MAINTENANCE = "SYSTEM_MAINTENANCE"
    SYSTEM_CONFIG_UPDATE = "SYSTEM_CONFIG_UPDATE"

    ELECTRIC_CHECK_SUCCESS = "ELECTRIC_CHECK_SUCCESS"
    ELECTRIC_CHECK_USER_NOT_FOUND = "ELECTRIC_CHECK_USER_NOT_FOUND"
    ELECTRIC_CHECK_INVALID_REQUEST = "ELECTRIC_CHECK_INVALID_REQUEST"
    ELECTRIC_CHECK_RETRIEVAL = "ELECTRIC_CHECK_RETRIEVAL"

    USER_REGISTER = "USER_REGISTER"
    USER_UPDATE = "USER_UPDATE"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    USER_DELETION = "USER_DELETION"

    NOTIFICATION_EMAIL_SENT = "NOTIFICATION_EMAIL_SENT"
    NOTIFICATION_TELEGRAM_SENT = "NOTIFICATION_TELEGRAM_SENT"
    NOTIFICATION_FAILED = "NOTIFICATION_FAILED"

    LICENSE_ACTIVATED = "LICENSE_ACTIVATED"
    LICENSE_DEACTIVATED = "LICENSE_DEACTIVATED"

    SECURITY_UNAUTHORIZED_ACCESS = "SECURITY_UNAUTHORIZED_ACCESS"
    SECURITY_LOGIN_FAILURE = "SECURITY_LOGIN_FAILURE"
    SECURITY_PASSWORD_RESET = "SECURITY_PASSWORD_RESET"

    ERROR_API = "ERROR_API"
    ERROR_DATABASE = "ERROR_DATABASE"
    ERROR_NOTIFICATION = "ERROR_NOTIFICATION"

    ADMIN_LOG_TYPE_LIST_VIEWED = "ADMIN_LOG_TYPE_LIST_VIEWED"
    ADMIN_USER_LIST_VIEWED = "ADMIN_USER_LIST_VIEWED"
    ADMIN_USER_REGISTERED = "ADMIN_USER_REGISTERED"
    ADMIN_USER_DELETED = "ADMIN_USER_DELETED"
    ADMIN_LOGS_VIEWED = "ADMIN_LOGS_VIEWED"
    ADMIN_LICENSE_ACTIVATED = "ADMIN_LICENSE_ACTIVATED"
    ADMIN_LICENSE_DEACTIVATED = "ADMIN_LICENSE_DEACTIVATED"
    ADMIN_PERIODIC_CHECK_STARTED = "ADMIN_PERIODIC_CHECK_STARTED"
    ADMIN_INACTIVE_USERS_NOTIFIED = "ADMIN_INACTIVE_USERS_NOTIFIED"
    ADMIN_TEST_EMAIL_SENT = "ADMIN_TEST_EMAIL_SENT"
    ADMIN_NOTIFICATION_SENT = "ADMIN_NOTIFICATION_SENT"


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(36), db.ForeignKey(
        'user.username'), nullable=True)
    log_type = db.Column(Enum(LogTypeEnum), nullable=False,
                         default=LogTypeEnum.ELECTRIC_CHECK_SUCCESS)

    def __repr__(self):
        return f'<Log {self.id} - {self.level}>'

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "username": self.username,
            "log_type": self.log_type.value if self.log_type else None
        }


def log_message(level, message, username=None, log_type=None):
    new_log = Log(level=level, message=message,
                  username=username, log_type=log_type)
    db.session.add(new_log)
    db.session.commit()
    if level == "ERROR":
        logger.error(f"{message} (User: {username})")
    else:
        logger.info(f"{message} (User: {username})")


async def send_information(subject, recipient, body, chat_id):
    try:
        # mail
        msg = Message(
            subject=subject,
            sender=str(app.config.get("MAIL_DEFAULT_SENDER")),
            recipients=[recipient],
            html=body
        )
        mail.send(msg)
        log_message(
            level="INFO", message=f"Email sent to {recipient}", username=None, log_type=LogTypeEnum.NOTIFICATION_EMAIL_SENT)
    except Exception as e:
        log_message(
            level="ERROR", message=f"Error while sending mail to : {recipient} - {str(e)}", log_type=LogTypeEnum.ERROR_NOTIFICATION)
    # telegram message
    try:
        message = await bot.send_message(chat_id=chat_id, text=body)
        log_message(
            level="INFO", message=f"Telegram message sent to {chat_id}", username=None, log_type=LogTypeEnum.NOTIFICATION_TELEGRAM_SENT)
    except Exception as e:
        log_message(
            level="ERROR", message=f"Error while sending telegram message to : {chat_id} - {str(e)}", log_type=LogTypeEnum.ERROR_NOTIFICATION)


@app.route('/')
@swag_from('swagger_specs/hello_world.yaml')
def hello_world():
    log_message(
        level="INFO",
        message="Hello World endpoint was accessed.",
        log_type=LogTypeEnum.SYSTEM_STARTUP
    )
    return jsonify(message='Hello World'), 200


@app.route('/health-check', methods=['GET'])
@swag_from('swagger_specs/health_check.yaml')
def health_check():
    log_message(
        level="INFO",
        message="Health check was performed.",
        log_type=LogTypeEnum.HEALTH_CHECK
    )
    return jsonify(status='OK', message="System Working!"), 200


@app.route('/detailed-health-check', methods=['GET'])
@swag_from('swagger_specs/detailed_health_check.yaml')
def detailed_health_check():
    try:
        db.session.execute(text('SELECT 1'))
        database_status = 'OK'
    except Exception as e:
        database_status = f'NOT OK: {str(e)}'

    try:
        telegram_status = asyncio.run(bot.get_me())
        telegram_status = 'OK' if telegram_status else 'NOT OK'
    except Exception as e:
        telegram_status = f'NOT OK: {str(e)}'

    health_status = {
        'database': database_status,
        'telegram_bot': telegram_status,
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
    return jsonify(health_status), 200


@app.route('/user/electric-check', methods=['POST'])
@swag_from('swagger_specs/electric_check_post.yaml')
def post_electric_check():
    data = request.get_json()
    username = data.get('username', None)

    if username is None:
        log_message(
            level="ERROR",
            message="Username is required for electric check.",
            log_type=LogTypeEnum.ELECTRIC_CHECK_INVALID_REQUEST
        )
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username, has_license=True).first()
    if user is None:
        log_message(
            level="ERROR",
            message="User not found for electric check.",
            username=username,
            log_type=LogTypeEnum.ELECTRIC_CHECK_USER_NOT_FOUND
        )
        return jsonify(message='User not found'), 404

    last_request_date = datetime.now()
    user.last_request_date = last_request_date
    db.session.commit()
    log_message(
        level="INFO",
        message="Electric check completed and last request date updated.",
        username=username,
        log_type=LogTypeEnum.ELECTRIC_CHECK_SUCCESS
    )
    return jsonify(status='OK', message='Last request date updated', data={'user': user.email, 'last_request_date': last_request_date.isoformat()}), 200


@app.route('/user/electric-check', methods=['GET'])
@swag_from('swagger_specs/electric_check_get.yaml')
def get_electric_check():
    username = request.args.get('username', None)

    if username is None:
        log_message(
            level="ERROR",
            message="Username is required for electric check retrieval.",
            log_type=LogTypeEnum.ELECTRIC_CHECK_INVALID_REQUEST
        )
        return jsonify(message='Username is required'), 400

    user = User.query.filter_by(username=username, has_license=True).first()
    if user is None:
        log_message(
            level="ERROR",
            message="User not found for electric check retrieval.",
            username=username,
            log_type=LogTypeEnum.ELECTRIC_CHECK_USER_NOT_FOUND
        )
        return jsonify(message='User not found'), 404

    log_message(
        level="INFO",
        message="Electric check retrieval successful.",
        username=username,
        log_type=LogTypeEnum.ELECTRIC_CHECK_RETRIEVAL
    )
    return jsonify(status='OK', message='Last request date retrieved', data={'user': user.email, 'last_request_date': user.last_request_date.isoformat() if user.last_request_date else None}), 200


@app.route('/admin/logs', methods=['GET'])
@swag_from('swagger_specs/logs_get.yaml')
def get_logs():
    admin_key_request = request.headers.get('admin-key', None)

    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for log retrieval.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message='Invalid or missing admin key'), 400

    page = request.headers.get('X-Page', 1, type=int)
    per_page = request.headers.get('X-Per-Page', 10, type=int)
    log_type = request.headers.get('X-Log-Type', "SYSTEM_STARTUP", type=str)

    try:
        logs_query = Log.query.filter_by(
            log_type=log_type).order_by(Log.timestamp.desc())
        paginated_logs = logs_query.paginate(
            page=page, per_page=per_page, error_out=False)

        logs_data = [log.to_dict() for log in paginated_logs.items]

        response_data = {
            'logs': logs_data,
            'pagination': {
                'page': paginated_logs.page,
                'per_page': paginated_logs.per_page,
                'total': paginated_logs.total,
                'pages': paginated_logs.pages,
            }
        }

        log_message(
            level="INFO",
            message="Logs retrieved successfully by admin.",
            log_type=LogTypeEnum.ADMIN_LOGS_VIEWED
        )
        return jsonify(status='OK', message='Logs retrieved successfully', data=response_data), 200

    except Exception as e:
        log_message(
            level="ERROR",
            message=f"Error during log retrieval: {str(e)}",
            log_type=LogTypeEnum.ERROR_API
        )
        return jsonify(status="NOK", message="An error occurred while retrieving logs"), 500


@app.route('/admin/users/list', methods=['GET'])
@swag_from('swagger_specs/users_list.yaml')
def users_list():
    admin_key_request = request.headers.get('admin-key', None)

    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for user list retrieval.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message='Operation Failed.'), 400

    users = User.query.all()
    if users:
        log_message(
            level="INFO",
            message="User list retrieved successfully by admin.",
            log_type=LogTypeEnum.ADMIN_USER_LIST_VIEWED
        )
        return jsonify(status='OK', message='Users retrieved successfully', data={'users': [user.to_dict() for user in users]}), 200

    log_message(
        level="INFO",
        message="No users found during admin user list retrieval.",
        log_type=LogTypeEnum.ADMIN_USER_LIST_VIEWED
    )
    return jsonify(status='OK', message='Users retrieved successfully', data={'users': []}), 200


@app.route('/admin/users/register', methods=['POST'])
@swag_from('swagger_specs/users_register.yaml')
def create_user():
    admin_key_request = request.headers.get('admin-key', None)

    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for user registration.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message='Invalid or missing admin key'), 400

    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')

    if not all([first_name, last_name, email, phone_number]):
        log_message(
            level="ERROR",
            message="Missing information for user registration.",
            log_type=LogTypeEnum.ERROR_API
        )
        return jsonify(status="NOK", message="Missing information"), 400

    if User.query.filter_by(email=email).first():
        log_message(
            level="ERROR",
            message="Email already registered during user registration.",
            log_type=LogTypeEnum.USER_REGISTER
        )
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
    log_message(
        level="INFO",
        message="New user registered successfully.",
        log_type=LogTypeEnum.ADMIN_USER_REGISTERED
    )
    return jsonify(status="OK", message="User created", data={'user': {'username': new_user.username, 'email': new_user.email}}), 201


@app.route('/admin/users/delete/', methods=['DELETE'])
@swag_from('swagger_specs/users_delete.yaml')
def delete_user():
    admin_key_request = request.headers.get('admin-key', None)
    if admin_key_request is None or admin_key_request != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for user deletion.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message='Invalid or missing admin key'), 400

    data = request.get_json()
    email = data.get('email', None)
    if email is None:
        log_message(
            level="ERROR",
            message="Email is required for user deletion.",
            log_type=LogTypeEnum.ERROR_API
        )
        return jsonify(status="NOK", message='Email is Required.'), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        log_message(
            level="ERROR",
            message="User not found for deletion.",
            log_type=LogTypeEnum.ADMIN_USER_DELETED
        )
        return jsonify(status="NOK", message='User not found'), 404

    db.session.delete(user)
    db.session.commit()
    log_message(
        level="INFO",
        message="User deleted successfully.",
        username=user.username,
        log_type=LogTypeEnum.ADMIN_USER_DELETED
    )
    return jsonify(status="OK", message='User deleted successfully'), 200


@app.route('/admin/license/deactivate/<username>', methods=['PATCH'])
@swag_from('swagger_specs/license_deactivate.yaml')
def deactivate_license(username):
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for deactivating license.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        log_message(
            level="ERROR",
            message=f"User {username} not found for license deactivation.",
            username=username,
            log_type=LogTypeEnum.ADMIN_LICENSE_DEACTIVATED
        )
        return jsonify(status="NOK", message="User not found"), 404

    user.has_license = False
    db.session.commit()
    log_message(
        level="INFO",
        message=f"License deactivated for user {username}.",
        username=username,
        log_type=LogTypeEnum.ADMIN_LICENSE_DEACTIVATED
    )
    return jsonify(status="OK", message="License deactivated"), 200


@app.route('/admin/license/activate/<username>', methods=['PATCH'])
@swag_from('swagger_specs/license_activate.yaml')
def activate_license(username):
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for activating license.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400

    user = User.query.filter_by(username=username).first()
    if user is None:
        log_message(
            level="ERROR",
            message=f"User {username} not found for license activation.",
            username=username,
            log_type=LogTypeEnum.ADMIN_LICENSE_ACTIVATED
        )
        return jsonify(status="NOK", message="User not found"), 404

    user.has_license = True
    db.session.commit()
    log_message(
        level="INFO",
        message=f"License activated for user {username}.",
        username=username,
        log_type=LogTypeEnum.ADMIN_LICENSE_ACTIVATED
    )
    return jsonify(status="OK", message="License activated"), 200


@app.route('/admin/send-test-email')
@swag_from('swagger_specs/send_test_email.yaml')
def send_test_email():
    try:
        log_message(
            level="INFO",
            message="Test email sent successfully.",
            log_type=LogTypeEnum.ADMIN_TEST_EMAIL_SENT
        )
        return "Email sent successfully!"
    except Exception as e:
        log_message(
            level="ERROR",
            message=f"Failed to send test email. Error: {str(e)}",
            log_type=LogTypeEnum.ERROR_NOTIFICATION
        )
        return "Failed to send email."


@app.route('/admin/periodic-check')
@swag_from('swagger_specs/periodic_check.yaml')
def periodic_check():
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for periodic check.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400

    two_hours_ago = datetime.now() - timedelta(hours=2)
    inactive_users = User.query.filter(
        User.last_request_date < two_hours_ago).all()
    log_message(
        level="INFO",
        message=f"Periodic check performed, found {len(inactive_users)} inactive users.",
        log_type=LogTypeEnum.ADMIN_PERIODIC_CHECK_STARTED
    )

    if inactive_users:
        for user in inactive_users:
            log_message(
                level="INFO",
                message=f"Sending notification to user {user.username}.",
                username=user.username,
                log_type=LogTypeEnum.ADMIN_INACTIVE_USERS_NOTIFIED
            )
            asyncio.run(send_information(
                subject="Dikkat!",
                recipient=user.email,
                chat_id=user.chat_id,
                body=Config.MAIL_BODY
            ))

    return "Periodic Check Started!"


@app.route('/admin/log-type/list')
@swag_from('swagger_specs/list_log_types.yaml')
def list_log_types():
    admin_key = request.headers.get('admin-key')

    if admin_key is None or admin_key != Config.ADMIN_KEY:
        log_message(
            level="ERROR",
            message="Invalid or missing admin key for periodic check.",
            log_type=LogTypeEnum.SECURITY_UNAUTHORIZED_ACCESS
        )
        return jsonify(status="NOK", message="Invalid or missing admin key"), 400

    log_types = [log_type.value for log_type in LogTypeEnum]
    log_message(
        level="INFO",
        message="Listed log types by admin.",
        log_type=LogTypeEnum.ADMIN_LOG_TYPE_LIST_VIEWED
    )
    return jsonify(status="OK", message="Log types listed.", data=log_types), 200


@app.route('/telegram/user-data', methods=['POST'], )
@swag_from('swagger_specs/user_data_post.yaml')
def create_user_with_telegram():
    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    chat_id = data.get('chat_id')

    if not all([first_name, last_name, email, phone_number, chat_id]):
        log_message(
            level="ERROR",
            message=f"Missing information - {first_name, last_name, email, phone_number, chat_id}.",
            log_type=LogTypeEnum.ERROR_API
        )
        return jsonify(status="NOK", message="Missing information"), 400

    user = User.query.filter(
        or_(
            User.chat_id == chat_id,
            User.phone_number == phone_number,
            User.email == email)).first()

    if user:
        log_message(
            level="INFO",
            message="User already registered.",
            username=user.username,
            log_type=LogTypeEnum.USER_REGISTER
        )
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
        log_message(
            level="INFO",
            message="User created successfully.",
            username=new_user.username,
            log_type=LogTypeEnum.USER_REGISTER
        )
        return jsonify(status="OK", message="User successfully created"), 201
    except Exception as e:
        log_message(
            level="ERROR",
            message=f"Exception occurred while creating user: {str(e)}.",
            log_type=LogTypeEnum.ERROR_API
        )
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
