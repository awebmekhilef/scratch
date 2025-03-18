"""Update game table

Revision ID: 5fdae3ee6326
Revises: 7de7df28016e
Create Date: 2025-03-18 23:14:26.617824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fdae3ee6326'
down_revision = '7de7df28016e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_column('slug')

    # ### end Alembic commands ###
