"""Add content column to posts table

Revision ID: 9155e71fc93c
Revises: 4108934fb378
Create Date: 2024-10-24 11:16:32.698610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9155e71fc93c'
down_revision: Union[str, None] = '4108934fb378'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
