"""add_mandi_history_and_cache_tables

Revision ID: b920a10b2mnd
Revises: 26a2e603f0b0
Create Date: 2026-10-30 10:30:00.000000+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b920a10b2mnd'
down_revision: Union[str, None] = '26a2e603f0b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    existing_tables = sa.inspect(conn).get_table_names()

    if 'mandi_price_history' not in existing_tables:
        op.create_table(
            'mandi_price_history',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('state', sa.String(length=100), nullable=False),
            sa.Column('district', sa.String(length=100), nullable=False),
            sa.Column('market', sa.String(length=150), nullable=False),
            sa.Column('commodity', sa.String(length=100), nullable=False),
            sa.Column('variety', sa.String(length=100), nullable=True),
            sa.Column('grade', sa.String(length=50), nullable=True),
            sa.Column('arrival_date', sa.String(length=20), nullable=False),
            sa.Column('min_price', sa.Float(), nullable=False),
            sa.Column('max_price', sa.Float(), nullable=False),
            sa.Column('modal_price', sa.Float(), nullable=False),
            sa.Column('recorded_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('state', 'district', 'market', 'commodity', 'variety', 'arrival_date', name='uq_mandi_history_entry')
        )
        op.create_index(op.f('ix_mandi_price_history_arrival_date'), 'mandi_price_history', ['arrival_date'], unique=False)
        op.create_index(op.f('ix_mandi_price_history_commodity'), 'mandi_price_history', ['commodity'], unique=False)
        op.create_index(op.f('ix_mandi_price_history_district'), 'mandi_price_history', ['district'], unique=False)
        op.create_index(op.f('ix_mandi_price_history_market'), 'mandi_price_history', ['market'], unique=False)
        op.create_index(op.f('ix_mandi_price_history_state'), 'mandi_price_history', ['state'], unique=False)

    if 'mandi_price_cache' not in existing_tables:
        op.create_table(
            'mandi_price_cache',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('cache_key', sa.String(length=255), nullable=False),
            sa.Column('response_json', sa.Text(), nullable=False),
            sa.Column('cached_at', sa.DateTime(), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_mandi_price_cache_cache_key'), 'mandi_price_cache', ['cache_key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_mandi_price_cache_cache_key'), table_name='mandi_price_cache')
    op.drop_table('mandi_price_cache')
    op.drop_index(op.f('ix_mandi_price_history_state'), table_name='mandi_price_history')
    op.drop_index(op.f('ix_mandi_price_history_market'), table_name='mandi_price_history')
    op.drop_index(op.f('ix_mandi_price_history_district'), table_name='mandi_price_history')
    op.drop_index(op.f('ix_mandi_price_history_commodity'), table_name='mandi_price_history')
    op.drop_index(op.f('ix_mandi_price_history_arrival_date'), table_name='mandi_price_history')
    op.drop_table('mandi_price_history')

