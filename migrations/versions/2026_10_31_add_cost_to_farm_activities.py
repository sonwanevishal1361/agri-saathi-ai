"""Add cost column to farm_activities table.

Revision ID: 2026_10_31_activity_cost
Revises: 2026_10_31_admin_role
Create Date: 2026-10-31 15:40:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2026_10_31_activity_cost'
down_revision = '2026_10_31_admin_role'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Add cost column to farm_activities if not present
    if 'farm_activities' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('farm_activities')]
        if 'cost' not in columns:
            op.add_column(
                'farm_activities',
                sa.Column('cost', sa.Float(), server_default='0.0', nullable=True)
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'farm_activities' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('farm_activities')]
        if 'cost' in columns:
            op.drop_column('farm_activities', 'cost')

