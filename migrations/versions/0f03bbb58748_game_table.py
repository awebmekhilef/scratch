"""Game table

Revision ID: 0f03bbb58748
Revises: 6361d0ebc53b
Create Date: 2025-03-15 15:39:09.198571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f03bbb58748'
down_revision = '6361d0ebc53b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_game_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_game_user_id'))
        batch_op.drop_index(batch_op.f('ix_game_created_at'))

    op.drop_table('game')
    # ### end Alembic commands ###
