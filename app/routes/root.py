from flask import Blueprint, jsonify
from app import db
from app.models.log import LogTypeEnum
from app.utils.logger import log_message
import asyncio
import psutil
from flasgger import swag_from
from sqlalchemy import text
from app import bot
from config import Config

root_bp = Blueprint('root', __name__)

@root_bp.route('/health-check', methods=['GET'])
@swag_from('../swagger_specs/health_check.yaml')
def health_check():
    log_message(
        level="INFO",
        message="Health check was performed.",
        log_type=LogTypeEnum.HEALTH_CHECK
    )
    return jsonify(status='OK', message="System Working!"), 200


@root_bp.route('/detailed-health-check', methods=['GET'])
@swag_from('../swagger_specs/detailed_health_check.yaml')
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


