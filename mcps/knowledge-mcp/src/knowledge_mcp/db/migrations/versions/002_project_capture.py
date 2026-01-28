"""Add project capture tables for workflow support.

Revision ID: 002
Revises: 001
Create Date: 2026-01-28 13:17:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create project capture tables: projects, query_history, decisions, decision_sources."""
    # Create projects table
    op.create_table(
        'projects',
        sa.Column(
            'id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column(
            'status',
            sa.String(length=50),
            nullable=False,
            server_default='planning',
        ),
        sa.Column('applicable_standards', sa.dialects.postgresql.ARRAY(sa.String()), nullable=True),
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
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "status IN ('planning', 'active', 'completed', 'abandoned')",
            name='project_status_check',
        ),
    )
    op.create_index(
        op.f('ix_projects_status'),
        'projects',
        ['status'],
        unique=False,
    )

    # Create query_history table
    op.create_table(
        'query_history',
        sa.Column(
            'id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'project_id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('result_count', sa.Integer(), nullable=False),
        sa.Column('workflow_type', sa.String(length=50), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['project_id'],
            ['projects.id'],
            name='fk_query_history_project_id',
            ondelete='CASCADE',
        ),
    )
    op.create_index(
        op.f('ix_query_history_project_id'),
        'query_history',
        ['project_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_query_history_workflow_type'),
        'query_history',
        ['workflow_type'],
        unique=False,
    )

    # Create decisions table
    op.create_table(
        'decisions',
        sa.Column(
            'id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'project_id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column('decision', sa.Text(), nullable=False),
        sa.Column('alternatives', sa.dialects.postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['project_id'],
            ['projects.id'],
            name='fk_decisions_project_id',
            ondelete='CASCADE',
        ),
    )
    op.create_index(
        op.f('ix_decisions_project_id'),
        'decisions',
        ['project_id'],
        unique=False,
    )

    # Create decision_sources table
    op.create_table(
        'decision_sources',
        sa.Column(
            'id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'decision_id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column('chunk_id', sa.String(length=255), nullable=False),
        sa.Column('relevance', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['decision_id'],
            ['decisions.id'],
            name='fk_decision_sources_decision_id',
            ondelete='CASCADE',
        ),
    )
    op.create_index(
        op.f('ix_decision_sources_decision_id'),
        'decision_sources',
        ['decision_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_decision_sources_chunk_id'),
        'decision_sources',
        ['chunk_id'],
        unique=False,
    )


def downgrade() -> None:
    """Drop project capture tables in reverse order."""
    # Drop decision_sources table
    op.drop_index(op.f('ix_decision_sources_chunk_id'), table_name='decision_sources')
    op.drop_index(op.f('ix_decision_sources_decision_id'), table_name='decision_sources')
    op.drop_table('decision_sources')

    # Drop decisions table
    op.drop_index(op.f('ix_decisions_project_id'), table_name='decisions')
    op.drop_table('decisions')

    # Drop query_history table
    op.drop_index(op.f('ix_query_history_workflow_type'), table_name='query_history')
    op.drop_index(op.f('ix_query_history_project_id'), table_name='query_history')
    op.drop_table('query_history')

    # Drop projects table
    op.drop_index(op.f('ix_projects_status'), table_name='projects')
    op.drop_table('projects')
