"""initial migration

Revision ID: 4a03d4a27c8d
Revises: 
Create Date: 2025-01-02 20:46:43.559032

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4a03d4a27c8d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.alter_column('log_type',
               existing_type=postgresql.ENUM('SYSTEM_STARTUP', 'SYSTEM_SHUTDOWN', 'SYSTEM_MAINTENANCE', 'SYSTEM_CONFIG_UPDATE', 'ELECTRIC_CHECK_SUCCESS', 'ELECTRIC_CHECK_USER_NOT_FOUND', 'ELECTRIC_CHECK_INVALID_REQUEST', 'ELECTRIC_CHECK_RETRIEVAL', 'USER_REGISTER', 'USER_UPDATE', 'USER_LOGIN', 'USER_LOGOUT', 'USER_DELETION', 'NOTIFICATION_EMAIL_SENT', 'NOTIFICATION_TELEGRAM_SENT', 'NOTIFICATION_FAILED', 'LICENSE_ACTIVATED', 'LICENSE_DEACTIVATED', 'SECURITY_UNAUTHORIZED_ACCESS', 'SECURITY_LOGIN_FAILURE', 'SECURITY_PASSWORD_RESET', 'ERROR_API', 'ERROR_DATABASE', 'ERROR_NOTIFICATION', 'ADMIN_USER_LIST_VIEWED', 'ADMIN_USER_REGISTERED', 'ADMIN_USER_DELETED', 'ADMIN_LOGS_VIEWED', 'ADMIN_LICENSE_ACTIVATED', 'ADMIN_LICENSE_DEACTIVATED', 'ADMIN_PERIODIC_CHECK_STARTED', 'ADMIN_INACTIVE_USERS_NOTIFIED', 'ADMIN_TEST_EMAIL_SENT', 'ADMIN_NOTIFICATION_SENT', name='log_type_enum'),
               type_=sa.Enum('SYSTEM_STARTUP', 'SYSTEM_SHUTDOWN', 'SYSTEM_MAINTENANCE', 'SYSTEM_CONFIG_UPDATE', 'ELECTRIC_CHECK_SUCCESS', 'ELECTRIC_CHECK_USER_NOT_FOUND', 'ELECTRIC_CHECK_INVALID_REQUEST', 'ELECTRIC_CHECK_RETRIEVAL', 'USER_REGISTER', 'USER_UPDATE', 'USER_LOGIN', 'USER_LOGOUT', 'USER_DELETION', 'NOTIFICATION_EMAIL_SENT', 'NOTIFICATION_TELEGRAM_SENT', 'NOTIFICATION_FAILED', 'LICENSE_ACTIVATED', 'LICENSE_DEACTIVATED', 'SECURITY_UNAUTHORIZED_ACCESS', 'SECURITY_LOGIN_FAILURE', 'SECURITY_PASSWORD_RESET', 'ERROR_API', 'ERROR_DATABASE', 'ERROR_NOTIFICATION', 'ADMIN_LOG_TYPE_LIST_VIEWED', 'ADMIN_USER_LIST_VIEWED', 'ADMIN_USER_REGISTERED', 'ADMIN_USER_DELETED', 'ADMIN_LOGS_VIEWED', 'ADMIN_LICENSE_ACTIVATED', 'ADMIN_LICENSE_DEACTIVATED', 'ADMIN_PERIODIC_CHECK_STARTED', 'ADMIN_INACTIVE_USERS_NOTIFIED', 'ADMIN_TEST_EMAIL_SENT', 'ADMIN_NOTIFICATION_SENT', name='logtypeenum'),
               existing_nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.alter_column('log_type',
               existing_type=sa.Enum('SYSTEM_STARTUP', 'SYSTEM_SHUTDOWN', 'SYSTEM_MAINTENANCE', 'SYSTEM_CONFIG_UPDATE', 'ELECTRIC_CHECK_SUCCESS', 'ELECTRIC_CHECK_USER_NOT_FOUND', 'ELECTRIC_CHECK_INVALID_REQUEST', 'ELECTRIC_CHECK_RETRIEVAL', 'USER_REGISTER', 'USER_UPDATE', 'USER_LOGIN', 'USER_LOGOUT', 'USER_DELETION', 'NOTIFICATION_EMAIL_SENT', 'NOTIFICATION_TELEGRAM_SENT', 'NOTIFICATION_FAILED', 'LICENSE_ACTIVATED', 'LICENSE_DEACTIVATED', 'SECURITY_UNAUTHORIZED_ACCESS', 'SECURITY_LOGIN_FAILURE', 'SECURITY_PASSWORD_RESET', 'ERROR_API', 'ERROR_DATABASE', 'ERROR_NOTIFICATION', 'ADMIN_LOG_TYPE_LIST_VIEWED', 'ADMIN_USER_LIST_VIEWED', 'ADMIN_USER_REGISTERED', 'ADMIN_USER_DELETED', 'ADMIN_LOGS_VIEWED', 'ADMIN_LICENSE_ACTIVATED', 'ADMIN_LICENSE_DEACTIVATED', 'ADMIN_PERIODIC_CHECK_STARTED', 'ADMIN_INACTIVE_USERS_NOTIFIED', 'ADMIN_TEST_EMAIL_SENT', 'ADMIN_NOTIFICATION_SENT', name='logtypeenum'),
               type_=postgresql.ENUM('SYSTEM_STARTUP', 'SYSTEM_SHUTDOWN', 'SYSTEM_MAINTENANCE', 'SYSTEM_CONFIG_UPDATE', 'ELECTRIC_CHECK_SUCCESS', 'ELECTRIC_CHECK_USER_NOT_FOUND', 'ELECTRIC_CHECK_INVALID_REQUEST', 'ELECTRIC_CHECK_RETRIEVAL', 'USER_REGISTER', 'USER_UPDATE', 'USER_LOGIN', 'USER_LOGOUT', 'USER_DELETION', 'NOTIFICATION_EMAIL_SENT', 'NOTIFICATION_TELEGRAM_SENT', 'NOTIFICATION_FAILED', 'LICENSE_ACTIVATED', 'LICENSE_DEACTIVATED', 'SECURITY_UNAUTHORIZED_ACCESS', 'SECURITY_LOGIN_FAILURE', 'SECURITY_PASSWORD_RESET', 'ERROR_API', 'ERROR_DATABASE', 'ERROR_NOTIFICATION', 'ADMIN_USER_LIST_VIEWED', 'ADMIN_USER_REGISTERED', 'ADMIN_USER_DELETED', 'ADMIN_LOGS_VIEWED', 'ADMIN_LICENSE_ACTIVATED', 'ADMIN_LICENSE_DEACTIVATED', 'ADMIN_PERIODIC_CHECK_STARTED', 'ADMIN_INACTIVE_USERS_NOTIFIED', 'ADMIN_TEST_EMAIL_SENT', 'ADMIN_NOTIFICATION_SENT', name='log_type_enum'),
               existing_nullable=False)

    # ### end Alembic commands ###
