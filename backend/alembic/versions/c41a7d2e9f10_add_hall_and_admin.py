"""add hall to capsules and admin flag to users

Revision ID: c41a7d2e9f10
Revises: b226325409b9
Create Date: 2026-10-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c41a7d2e9f10'
down_revision: Union[str, None] = 'b226325409b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.alter_column('users', 'name', type_=sa.String(length=20), existing_nullable=False)

    # lâmpadas que já existiam vão para o salão asiático
    op.add_column('capsules', sa.Column('hall', sa.String(length=20), server_default='asiatico', nullable=False))
    op.alter_column('capsules', 'hall', server_default=None)
    op.alter_column('capsules', 'title', type_=sa.String(length=80), existing_nullable=False)
    op.alter_column('capsules', 'content', type_=sa.String(length=1000), existing_nullable=False)
    op.create_index(op.f('ix_capsules_hall'), 'capsules', ['hall'], unique=False)
    op.create_index(op.f('ix_capsules_open_at'), 'capsules', ['open_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_capsules_open_at'), table_name='capsules')
    op.drop_index(op.f('ix_capsules_hall'), table_name='capsules')
    op.alter_column('capsules', 'content', type_=sa.String(), existing_nullable=False)
    op.alter_column('capsules', 'title', type_=sa.String(), existing_nullable=False)
    op.drop_column('capsules', 'hall')
    op.alter_column('users', 'name', type_=sa.String(), existing_nullable=False)
    op.drop_column('users', 'is_admin')
