"""add_curriculum_readiness_metadata_to_subjects

Revision ID: c1a2e3f4b5d6
Revises: 244570d98dae
Create Date: 2026-09-23 02:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a2e3f4b5d6'
down_revision: Union[str, Sequence[str], None] = '244570d98dae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add curriculum readiness and source provenance metadata."""
    op.add_column(
        'subjects',
        sa.Column(
            'curriculum_status',
            sa.String(length=50),
            server_default='in_preparation',
            nullable=False,
        ),
    )
    op.add_column(
        'subjects',
        sa.Column('source_authority', sa.String(length=150), nullable=True),
    )
    op.add_column(
        'subjects',
        sa.Column('source_url', sa.String(length=500), nullable=True),
    )
    op.add_column(
        'subjects',
        sa.Column('syllabus_version', sa.String(length=100), nullable=True),
    )
    op.add_column(
        'subjects',
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Initialize existing verified ISC Class 11 History slice
    op.execute(
        """
        UPDATE subjects
        SET curriculum_status = 'content_available',
            source_authority = 'CISCE',
            source_url = 'https://www.cisce.org/regulations-and-syllabuses-isc/',
            syllabus_version = 'Examination Year 2027',
            last_verified_at = NOW()
        WHERE code = 'isc-11-hist';
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('subjects', 'last_verified_at')
    op.drop_column('subjects', 'syllabus_version')
    op.drop_column('subjects', 'source_url')
    op.drop_column('subjects', 'source_authority')
    op.drop_column('subjects', 'curriculum_status')
