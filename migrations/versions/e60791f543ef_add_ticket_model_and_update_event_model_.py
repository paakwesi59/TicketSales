"""Add Ticket model and update Event model for ticket purchases

Revision ID: e60791f543ef
Revises: dafb4ce8ab63
Create Date: 2025-02-12 01:01:06.666319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e60791f543ef'
down_revision = 'dafb4ce8ab63'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_code', sa.String(length=36), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('purchaser_email', sa.String(length=120), nullable=False),
    sa.Column('purchase_time', sa.DateTime(), nullable=True),
    sa.Column('qr_code_filename', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ticket_code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ticket')
    # ### end Alembic commands ###
