"""addedwish_progress

Revision ID: dda24ac8ca9d
Revises: 76a60f58e11d
Create Date: 2017-07-10 16:11:55.326000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dda24ac8ca9d'
down_revision = '76a60f58e11d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wishes', sa.Column('wish_progress', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('wishes', 'wish_progress')
    # ### end Alembic commands ###
