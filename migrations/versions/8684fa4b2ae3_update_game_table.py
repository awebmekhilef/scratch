"""Update game table

Revision ID: 8684fa4b2ae3
Revises: 574022d2c33a
Create Date: 2025-03-19 16:42:39.610175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8684fa4b2ae3'
down_revision = '574022d2c33a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('upload',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filepath', sa.String(length=256), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('upload', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_upload_game_id'), ['game_id'], unique=False)

    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_column('game_file_path')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game_file_path', sa.VARCHAR(length=256), nullable=False))

    with op.batch_alter_table('upload', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_upload_game_id'))

    op.drop_table('upload')
    # ### end Alembic commands ###
