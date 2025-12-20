"""merge heads: e8f7d6c5b4a3, loan_return_inspection

Revision ID: merge_e8f7_loan_return
Revises: e8f7d6c5b4a3, loan_return_inspection
Create Date: 2025-12-20 09:xx:xx.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_e8f7_loan_return'
down_revision = ('e8f7d6c5b4a3', 'loan_return_inspection')
branch_labels = None
depend_on = None


def upgrade():
    # This is a merge revision to resolve multiple heads. No DB operations required here.
    pass


def downgrade():
    # Downgrade not supported for merge-only revision
    pass
