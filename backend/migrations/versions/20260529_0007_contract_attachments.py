"""contract attachments

Revision ID: 20260529_0007
Revises: 20260527_0006
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op

revision = "20260529_0007"
down_revision = "20260527_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contract_attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Uuid(), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("nome_arquivo", sa.String(length=255), nullable=False),
        sa.Column("caminho_storage", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], name=op.f("fk_contract_attachments_contract_id_contracts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], name=op.f("fk_contract_attachments_uploaded_by_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contract_attachments")),
    )
    op.create_index(op.f("ix_contract_attachments_contract_id"), "contract_attachments", ["contract_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_contract_attachments_contract_id"), table_name="contract_attachments")
    op.drop_table("contract_attachments")
