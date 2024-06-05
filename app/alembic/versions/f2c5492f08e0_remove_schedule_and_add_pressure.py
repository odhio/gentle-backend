"""remove schedule and add pressure

Revision ID: f2c5492f08e0
Revises: 9c32618a8499
Create Date: 2024-06-04 11:16:59.060619

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2c5492f08e0"
down_revision: Union[str, None] = "9c32618a8499"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    スケジューラ機能は直近必要なさそうなので削除し、分析に必要な音圧レコードのみ残す変更です。
    """
    op.add_column("messages", sa.Column("pressure", sa.REAL, nullable=False, server_default="0.0"))


def downgrade() -> None:
    op.drop_column("messages", "pressure")
