"""create assessments and symptom_responses tables

Revision ID: c243bf08b89a
Revises: 90c86b22f0a8
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c243bf08b89a'
down_revision: Union[str, Sequence[str], None] = '90c86b22f0a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    risk_level_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risklevel')

    op.create_table(
        'assessments',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('risk_level', risk_level_enum, nullable=False),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('image_analysis_result', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'symptom_responses',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('assessment_id', sa.UUID(), nullable=False),
        sa.Column('symptom_key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('assessment_id', 'symptom_key'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('symptom_responses')
    op.drop_table('assessments')
    sa.Enum(name='risklevel').drop(op.get_bind(), checkfirst=True)
