"""initial migration

Revision ID: 322794102059
Revises: 89dcaf67ca1c
Create Date: 2025-02-06 08:27:49.113669

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '322794102059'
down_revision = '89dcaf67ca1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=150),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=60),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('user_type',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=50),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('user_type',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(length=20),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=60),
               existing_nullable=False)
        batch_op.alter_column('username',
               existing_type=sa.String(length=150),
               type_=mysql.VARCHAR(length=20),
               existing_nullable=False)

    # ### end Alembic commands ###
