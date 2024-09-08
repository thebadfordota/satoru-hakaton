"""device_id

Revision ID: be47e8942289
Revises: 2fb10a3965ed
Create Date: 2024-09-07 17:00:37.347114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be47e8942289'
down_revision: Union[str, None] = '2fb10a3965ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('device_id', sa.String(length=36), nullable=True, default=None, comment='Id девайса'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'device_id')
    # ### end Alembic commands ###