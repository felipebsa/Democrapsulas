"""add capsule lantern

Revision ID: f3b7c2d91a04
Revises: 065cf0d75621
Create Date: 2026-10-27 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3b7c2d91a04'
down_revision: Union[str, None] = '065cf0d75621'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('capsules', sa.Column('lantern', sa.SmallInteger(), nullable=True))
    #capsules created before the lantern picker get a random one of the 17
    op.execute("update capsules set lantern = floor(random() * 17)::int + 1")
    op.alter_column('capsules', 'lantern', nullable=False)


def downgrade() -> None:
    op.drop_column('capsules', 'lantern')
