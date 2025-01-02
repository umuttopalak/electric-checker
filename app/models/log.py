from datetime import datetime
from enum import Enum as PyEnum
from app import db
from sqlalchemy import Enum

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
    username = db.Column(db.String(36), db.ForeignKey('user.username'), nullable=True)
    log_type = db.Column(
        Enum(LogTypeEnum, name='logtypeenum', create_type=False),
        nullable=False,
        default=LogTypeEnum.ELECTRIC_CHECK_SUCCESS
    )

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