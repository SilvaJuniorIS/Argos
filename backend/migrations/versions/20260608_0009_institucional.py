"""institucional config

Revision ID: 20260608_0009
Revises: 20260602_0008
Create Date: 2026-06-08
"""

import sqlalchemy as sa
from alembic import op

revision = "20260608_0009"
down_revision = "20260602_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "institucional",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome_orgao", sa.String(length=220), nullable=False),
        sa.Column("nome_municipio", sa.String(length=160), nullable=True),
        sa.Column("uf", sa.String(length=2), nullable=True),
        sa.Column("cnpj", sa.String(length=30), nullable=True),
        sa.Column("endereco", sa.String(length=300), nullable=True),
        sa.Column("telefone", sa.String(length=80), nullable=True),
        sa.Column("email", sa.String(length=160), nullable=True),
        sa.Column("site", sa.String(length=160), nullable=True),
        sa.Column("autoridade_nome", sa.String(length=180), nullable=True),
        sa.Column("autoridade_cargo", sa.String(length=120), nullable=True),
        sa.Column("responsavel_tecnico", sa.String(length=180), nullable=True),
        sa.Column("rodape_documentos", sa.Text(), nullable=True),
        sa.Column("logo_base64", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("institucional")
