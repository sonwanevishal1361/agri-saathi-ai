"""Add security columns (must_change_password, failed_login_attempts, locked_until) to users table.

Revision ID: 2026_10_31_user_security
Revises: 2026_10_31_activity_cost
Create Date: 2026-10-31 17:45:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2026_10_31_user_security'
down_revision = '2026_10_31_activity_cost'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'users' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('users')]
        with op.batch_alter_table('users') as batch_op:
            if 'must_change_password' not in columns:
                batch_op.add_column(
                    sa.Column('must_change_password', sa.Boolean(), server_default=sa.false(), nullable=False)
                )
            if 'failed_login_attempts' not in columns:
                batch_op.add_column(
                    sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False)
                )
            if 'locked_until' not in columns:
                batch_op.add_column(
                    sa.Column('locked_until', sa.DateTime(), nullable=True)
                )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'users' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('users')]
        with op.batch_alter_table('users') as batch_op:
            if 'locked_until' in columns:
                batch_op.drop_column('locked_until')
            if 'failed_login_attempts' in columns:
                batch_op.drop_column('failed_login_attempts')
            if 'must_change_password' in columns:
                batch_op.drop_column('must_change_password')

