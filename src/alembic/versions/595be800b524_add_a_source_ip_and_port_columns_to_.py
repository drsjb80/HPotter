"""Add a source ip and port columns to generic

Revision ID: 595be800b524
Revises: 
Create Date: 2016-05-30 12:19:05.192426

"""

# revision identifiers, used by Alembic.
revision = '595be800b524'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('generic', sa.Column('source_address', sa.String))
    op.add_column('generic', sa.Column('source_port', sa.Integer))

def downgrade():
    with op.batch_alter_table("generic") as batch_op:
        batch_op.drop_column('source_address')
        batch_op.drop_column('source_port')
