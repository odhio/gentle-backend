"""add a schedule column

Revision ID: ae0411eefd17
Revises: 9c32618a8499
Create Date: 2024-05-16 11:08:35.774998

"""

from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ae0411eefd17"
down_revision: Union[str, None] = "9c32618a8499"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("google_schedule", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("rooms", "google_schedule")
    pass
