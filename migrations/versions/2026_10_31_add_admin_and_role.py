"""Add user role column and admin_audit_logs table.

Revision ID: 2026_10_31_admin_role
Revises: 2026_10_30_mandi_history
Create Date: 2026-10-31 14:52:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2026_10_31_admin_role'
down_revision = '2026_10_30_mandi_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. Add role column to users if not present
    if 'users' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('users')]
        if 'role' not in columns:
            op.add_column(
                'users',
                sa.Column('role', sa.String(length=20), server_default='farmer', nullable=False)
            )
            op.create_index('ix_users_role', 'users', ['role'])

    # 2. Create admin_audit_logs if not present
    if 'admin_audit_logs' not in existing_tables:
        op.create_table(
            'admin_audit_logs',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('admin_id', sa.String(length=36), nullable=True),
            sa.Column('admin_name', sa.String(length=100), nullable=False),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('resource_type', sa.String(length=50), nullable=False),
            sa.Column('resource_id', sa.String(length=100), nullable=True),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('ip_address', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_admin_audit_logs_action', 'admin_audit_logs', ['action'])
        op.create_index('ix_admin_audit_logs_admin_id', 'admin_audit_logs', ['admin_id'])
        op.create_index('ix_admin_audit_logs_created_at', 'admin_audit_logs', ['created_at'])
        op.create_index('ix_admin_audit_logs_resource_type', 'admin_audit_logs', ['resource_type'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'admin_audit_logs' in existing_tables:
        op.drop_table('admin_audit_logs')

    if 'users' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('users')]
        if 'role' in columns:
            op.drop_column('users', 'role')
