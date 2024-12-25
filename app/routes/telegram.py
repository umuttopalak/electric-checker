from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from app.models.log import LogTypeEnum
from app.utils.logger import log_message
from sqlalchemy import or_
from flasgger import swag_from

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/user-data', methods=['POST'])
@swag_from('../swagger_specs/telegram_user_data.yaml')
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
            User.email == email
        )).first()

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