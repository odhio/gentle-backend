"""add a pressure column

Revision ID: a4fbdc8b42f7
Revises: ae0411eefd17
Create Date: 2024-05-31 23:43:25.956517

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4fbdc8b42f7"
down_revision: Union[str, None] = "ae0411eefd17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("pressure", sa.REAL, nullable=False, server_default="0.0"))


def downgrade() -> None:
    op.drop_column("messages", "pressure")
    pass
