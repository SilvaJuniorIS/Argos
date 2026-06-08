"""secretaria email alertas

Revision ID: 20260602_0008
Revises: 20260529_0007
Create Date: 2026-06-02
"""

import sqlalchemy as sa
from alembic import op

revision = "20260602_0008"
down_revision = "20260529_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("secretarias", sa.Column("email_alertas", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("secretarias", "email_alertas")
