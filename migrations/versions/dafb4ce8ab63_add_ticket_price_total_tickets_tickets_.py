"""Add ticket price, total tickets, tickets sold, and event image fields to Event model

Revision ID: dafb4ce8ab63
Revises: ed176343567b
Create Date: 2025-02-10 01:28:08.062991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dafb4ce8ab63'
down_revision = 'ed176343567b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tickets_sold', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('tickets_sold')

    # ### end Alembic commands ###
