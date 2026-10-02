"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Strategies table
    op.create_table(
        'strategies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('market', sa.String(50), nullable=False),
        sa.Column('timeframe', sa.String(20), nullable=False),
        sa.Column('graph', postgresql.JSONB(), nullable=False),
        sa.Column('current_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_strategies_user_id', 'strategies', ['user_id'], unique=False)
    op.create_index('ix_strategies_market', 'strategies', ['market'], unique=False)
    op.create_index('ix_strategies_user_market', 'strategies', ['user_id', 'market'], unique=False)

    # Strategy Versions table
    op.create_table(
        'strategy_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('strategy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('graph', postgresql.JSONB(), nullable=False),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('client', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('strategy_id', 'version', name='uq_strategy_version'),
    )
    op.create_index('ix_strategy_versions_strategy_id', 'strategy_versions', ['strategy_id'], unique=False)

    # Backtests table
    op.create_table(
        'backtests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('strategy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('strategy_version_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('metrics', postgresql.JSONB(), nullable=True),
        sa.Column('equity_curve', postgresql.JSONB(), nullable=True),
        sa.Column('trades', postgresql.JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['strategy_version_id'], ['strategy_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_backtests_strategy_id', 'backtests', ['strategy_id'], unique=False)
    op.create_index('ix_backtests_strategy_version_id', 'backtests', ['strategy_version_id'], unique=False)
    op.create_index('ix_backtests_strategy_status', 'backtests', ['strategy_id', 'status'], unique=False)

    # Datasets table
    op.create_table(
        'datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('market', sa.String(50), nullable=False),
        sa.Column('timeframe', sa.String(20), nullable=False),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('row_count', sa.BigInteger(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('market', 'timeframe', 'source', 'start_date', 'end_date', name='uq_dataset'),
    )
    op.create_index('ix_datasets_market_timeframe', 'datasets', ['market', 'timeframe'], unique=False)

    # Experiments table
    op.create_table(
        'experiments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('strategy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('base_version', sa.Integer(), nullable=False),
        sa.Column('candidate_version', sa.Integer(), nullable=False),
        sa.Column('hypothesis', sa.Text(), nullable=True),
        sa.Column('changes', postgresql.JSONB(), nullable=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('backtest_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('results', postgresql.JSONB(), nullable=True),
        sa.Column('conclusion', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('client', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['backtest_id'], ['backtests.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_experiments_strategy_id', 'experiments', ['strategy_id'], unique=False)


def downgrade() -> None:
    op.drop_table('experiments')
    op.drop_table('datasets')
    op.drop_table('backtests')
    op.drop_table('strategy_versions')
    op.drop_table('strategies')
    op.drop_table('users')