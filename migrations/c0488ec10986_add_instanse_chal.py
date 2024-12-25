"""add instance

Revision ID: c0488ec10986
Revises: 
Create Date: 2024-12-25 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0488ec10986'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(op=None):
    op.create_table(
        "instance_challenge",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("api", sa.Text, default='http://localhost:80'),
        sa.Column("apikey", sa.Text, default=''),
        sa.ForeignKeyConstraint(["id"], ["dynamic_challenge.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade(op=None) -> None:
    op.drop_table("instance_challenge")
