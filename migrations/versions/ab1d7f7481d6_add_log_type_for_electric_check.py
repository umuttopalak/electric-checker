"""Add log type for electric check

Revision ID: ab1d7f7481d6
Revises: 4cf1827d846f
Create Date: 2024-11-15 21:45:43.460571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab1d7f7481d6'
down_revision = '4cf1827d846f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('log_type', sa.Enum('SYSTEM_STARTUP', 'SYSTEM_SHUTDOWN', 'SYSTEM_MAINTENANCE', 'SYSTEM_CONFIG_UPDATE', 'ELECTRIC_CHECK_SUCCESS', 'ELECTRIC_CHECK_USER_NOT_FOUND', 'ELECTRIC_CHECK_INVALID_REQUEST', 'ELECTRIC_CHECK_RETRIEVAL', 'USER_REGISTER', 'USER_UPDATE', 'USER_LOGIN', 'USER_LOGOUT', 'USER_DELETION', 'NOTIFICATION_EMAIL_SENT', 'NOTIFICATION_TELEGRAM_SENT', 'NOTIFICATION_FAILED', 'LICENSE_ACTIVATED', 'LICENSE_DEACTIVATED', 'SECURITY_UNAUTHORIZED_ACCESS', 'SECURITY_LOGIN_FAILURE', 'SECURITY_PASSWORD_RESET', 'ERROR_API', 'ERROR_DATABASE', 'ERROR_NOTIFICATION', 'ADMIN_USER_LIST_VIEWED', 'ADMIN_USER_REGISTERED', 'ADMIN_USER_DELETED', 'ADMIN_LOGS_VIEWED', 'ADMIN_LICENSE_ACTIVATED', 'ADMIN_LICENSE_DEACTIVATED', 'ADMIN_PERIODIC_CHECK_STARTED', 'ADMIN_INACTIVE_USERS_NOTIFIED', 'ADMIN_TEST_EMAIL_SENT', 'ADMIN_NOTIFICATION_SENT', name='logtypeenum'), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.drop_column('log_type')

    # ### end Alembic commands ###