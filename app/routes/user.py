from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from app.models.log import LogTypeEnum
from app.utils.logger import log_message
from datetime import datetime
from flasgger import swag_from

user_bp = Blueprint('user', __name__)

@user_bp.route('/electric-check', methods=['POST'])
@swag_from('../swagger_specs/electric_check_post.yaml')
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


@user_bp.route('/electric-check', methods=['GET'])
@swag_from('../swagger_specs/electric_check_get.yaml')
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
