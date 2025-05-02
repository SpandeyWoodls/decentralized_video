# decentralized_video/migrations/versions/0001_initial.py
"""
Initial database schema migration
Revision ID: 0001_initial
Revises: 
Create Date: 2025-05-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('uploader', sa.String(), nullable=False),
        sa.Column('video_hash', sa.String(), unique=True, nullable=False),
        sa.Column('metadata_uri', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('cid', sa.String(), nullable=False),
        sa.Column('index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

    # Create nodes table
    op.create_table(
        'nodes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('capacity_gb', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

    # Create proofs table
    op.create_table(
        'proofs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('node_id', sa.String(), sa.ForeignKey('nodes.id'), nullable=False),
        sa.Column('cid', sa.String(), nullable=False),
        sa.Column('proof', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )


def downgrade():
    op.drop_table('proofs')
    op.drop_table('nodes')
    op.drop_table('chunks')
    op.drop_table('videos')
