"""merging last 2 changes

Revision ID: 36f1759eb4ee
Revises: 8681bd405755, 9886dbeaba0d
Create Date: 2018-09-19 23:38:45.433808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36f1759eb4ee'
down_revision = ('8681bd405755', '9886dbeaba0d')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
