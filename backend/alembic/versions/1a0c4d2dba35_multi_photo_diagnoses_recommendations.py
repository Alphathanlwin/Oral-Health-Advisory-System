"""multi-photo assessments + diagnoses/recommendations tables

Revision ID: 1a0c4d2dba35
Revises: c243bf08b89a
Create Date: 2026-08-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1a0c4d2dba35'
down_revision: Union[str, Sequence[str], None] = 'c243bf08b89a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Passed straight into the columns below (not .create()'d up front) —
    # op.create_table() creates enum types as a side effect of the column
    # DDL; calling .create() explicitly as well double-creates them.
    condition_enum = sa.Enum(
        'DENTAL_CAVITY', 'GINGIVITIS', 'TOOTH_ABSCESS', 'ENAMEL_EROSION',
        'CANKER_SORES', 'TOOTH_SENSITIVITY', name='condition',
    )
    urgency_enum = sa.Enum(
        'IMMEDIATE', 'WITHIN_1_WEEK', 'WITHIN_1_MONTH', 'MONITOR_AT_HOME', name='urgency',
    )

    # Phase 3D: guided capture replaced the single optional photo with three
    # (front/upper/lower). Old single-photo rows have no way to be split
    # into the new shape, so this drops photo_url rather than migrating it —
    # acceptable pre-launch (no production assessment data depends on it yet).
    op.add_column('assessments', sa.Column('photo_urls', postgresql.JSONB(), nullable=True))
    op.drop_column('assessments', 'photo_url')

    op.create_table(
        'diagnoses',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('assessment_id', sa.UUID(), nullable=False),
        sa.Column('condition', condition_enum, nullable=False),
        sa.Column('triggered_rules', postgresql.JSONB(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'recommendations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('diagnosis_id', sa.UUID(), nullable=False),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('urgency', urgency_enum, nullable=False),
        sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('recommendations')
    op.drop_table('diagnoses')

    op.add_column('assessments', sa.Column('photo_url', sa.String(length=500), nullable=True))
    op.drop_column('assessments', 'photo_urls')

    sa.Enum(name='urgency').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='condition').drop(op.get_bind(), checkfirst=True)
