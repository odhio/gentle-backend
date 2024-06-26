"""empty message

Revision ID: 9c32618a8499
Revises: 8f7dcde64369
Create Date: 2024-05-12 09:42:20.687442

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c32618a8499"
down_revision: Union[str, None] = "8f7dcde64369"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "dreams",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_dreams_uuid"), "dreams", ["uuid"], unique=False)
    op.create_table(
        "milestones",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("dream_uuid", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["dream_uuid"],
            ["dreams.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_milestones_uuid"), "milestones", ["uuid"], unique=False)
    op.create_table(
        "current_milestones",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("milestone_uuid", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["milestone_uuid"],
            ["milestones.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(
        op.f("ix_current_milestones_uuid"), "current_milestones", ["uuid"], unique=False
    )
    op.add_column("rooms", sa.Column("milestone_uuid", sa.String(), nullable=True))
    op.create_foreign_key(None, "rooms", "milestones", ["milestone_uuid"], ["uuid"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "rooms", type_="foreignkey")
    op.drop_column("rooms", "milestone_uuid")
    op.drop_index(op.f("ix_current_milestones_uuid"), table_name="current_milestones")
    op.drop_table("current_milestones")
    op.drop_index(op.f("ix_milestones_uuid"), table_name="milestones")
    op.drop_table("milestones")
    op.drop_index(op.f("ix_dreams_uuid"), table_name="dreams")
    op.drop_table("dreams")
    # ### end Alembic commands ###
