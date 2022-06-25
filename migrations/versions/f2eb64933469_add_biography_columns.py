"""Add biography_columns

Revision ID: f2eb64933469
Revises: 9066f8ca07ff
Create Date: 2022-06-23 18:01:03.097042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2eb64933469'
down_revision = '9066f8ca07ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('authors', sa.Column('portrait', sa.LargeBinary(), nullable=True))
    op.add_column('authors', sa.Column('biography_text', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('authors', 'biography_text')
    op.drop_column('authors', 'portrait')
    # ### end Alembic commands ###