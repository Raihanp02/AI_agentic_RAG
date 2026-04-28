"""create langgraph schema

Revision ID: 00b780e15d22
Revises: 1ff734a3a2fc
Create Date: 2026-04-22 17:51:33.429378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00b780e15d22'
down_revision: Union[str, Sequence[str], None] = '1ff734a3a2fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS langgraph")

def downgrade():
    op.execute("DROP SCHEMA IF EXISTS langgraph CASCADE")
