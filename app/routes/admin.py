from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from app.models.log import Log, LogTypeEnum
from app.utils.logger import log_message
from app.utils.notifications import send_information
from config import Config
from datetime import datetime, timedelta
import asyncio
from flasgger import swag_from

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/logs', methods=['GET'])
@swag_from('../swagger_specs/logs_get.yaml')
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


@admin_bp.route('/users/list', methods=['GET'])
@swag_from('../swagger_specs/users_list.yaml')
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


@admin_bp.route('/users/register', methods=['POST'])
@swag_from('../swagger_specs/users_register.yaml')
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


@admin_bp.route('/users/delete/', methods=['DELETE'])
@swag_from('../swagger_specs/users_delete.yaml')
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


@admin_bp.route('/license/deactivate/<username>', methods=['PATCH'])
@swag_from('../swagger_specs/license_deactivate.yaml')
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


@admin_bp.route('/license/activate/<username>', methods=['PATCH'])
@swag_from('../swagger_specs/license_activate.yaml')
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


@admin_bp.route('/send-test-email')
@swag_from('../swagger_specs/send_test_email.yaml')
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


@admin_bp.route('/periodic-check')
@swag_from('../swagger_specs/periodic_check.yaml')
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


@admin_bp.route('/log-type/list')
@swag_from('../swagger_specs/list_log_types.yaml')
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
