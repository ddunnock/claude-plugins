"""Initial schema with sources and acquisition_requests tables.

Revision ID: 001
Revises:
Create Date: 2026-01-27 13:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema with sources and acquisition_requests tables."""
    # Create acquisition_requests table
    op.create_table(
        'acquisition_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='3'),
        sa.Column(
            'status',
            sa.String(length=20),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('requested_by', sa.String(length=256), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'completed')",
            name='acquisition_request_status_check',
        ),
    )
    op.create_index(
        op.f('ix_acquisition_requests_url'),
        'acquisition_requests',
        ['url'],
        unique=False,
    )
    op.create_index(
        op.f('ix_acquisition_requests_status'),
        'acquisition_requests',
        ['status'],
        unique=False,
    )
    op.create_index(
        op.f('ix_acquisition_requests_priority'),
        'acquisition_requests',
        ['priority'],
        unique=False,
    )

    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('source_type', sa.String(length=20), nullable=False),
        sa.Column(
            'status',
            sa.String(length=20),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('authority_tier', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('last_crawled_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url'),
        sa.CheckConstraint(
            "source_type IN ('website', 'documentation', 'standards_body', 'blog', 'repository')",
            name='source_type_check',
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'failed', 'archived')",
            name='source_status_check',
        ),
        sa.CheckConstraint(
            "authority_tier IN ('tier_1_canonical', 'tier_2_trusted', 'tier_3_community')",
            name='authority_tier_check',
        ),
    )
    op.create_index(
        op.f('ix_sources_url'), 'sources', ['url'], unique=True
    )
    op.create_index(
        op.f('ix_sources_source_type'), 'sources', ['source_type'], unique=False
    )
    op.create_index(
        op.f('ix_sources_status'), 'sources', ['status'], unique=False
    )
    op.create_index(
        op.f('ix_sources_authority_tier'), 'sources', ['authority_tier'], unique=False
    )


def downgrade() -> None:
    """Drop sources and acquisition_requests tables."""
    op.drop_index(op.f('ix_sources_authority_tier'), table_name='sources')
    op.drop_index(op.f('ix_sources_status'), table_name='sources')
    op.drop_index(op.f('ix_sources_source_type'), table_name='sources')
    op.drop_index(op.f('ix_sources_url'), table_name='sources')
    op.drop_table('sources')

    op.drop_index(op.f('ix_acquisition_requests_priority'), table_name='acquisition_requests')
    op.drop_index(op.f('ix_acquisition_requests_status'), table_name='acquisition_requests')
    op.drop_index(op.f('ix_acquisition_requests_url'), table_name='acquisition_requests')
    op.drop_table('acquisition_requests')
