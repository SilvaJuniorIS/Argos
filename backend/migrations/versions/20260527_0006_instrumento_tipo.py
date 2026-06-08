"""instrumento tipo para contratos e atas

Revision ID: 20260527_0006
Revises: 20260526_0005
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa

revision = "20260527_0006"
down_revision = "20260526_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "contracts",
        sa.Column("tipo_instrumento", sa.String(length=40), server_default="contrato", nullable=False),
    )
    op.create_index(op.f("ix_contracts_tipo_instrumento"), "contracts", ["tipo_instrumento"], unique=False)
    op.create_index(
        "ix_contracts_tipo_numero",
        "contracts",
        ["tipo_instrumento", "numero_contrato"],
        unique=False,
    )

    op.add_column(
        "contratos",
        sa.Column("tipo_instrumento", sa.String(length=40), server_default="contrato", nullable=False),
    )
    op.create_index(op.f("ix_contratos_tipo_instrumento"), "contratos", ["tipo_instrumento"], unique=False)
    op.drop_constraint(op.f("uq_contratos_numero"), "contratos", type_="unique")
    op.create_unique_constraint(
        "uq_contratos_tipo_numero",
        "contratos",
        ["tipo_instrumento", "numero"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_contratos_tipo_numero", "contratos", type_="unique")
    op.create_unique_constraint(op.f("uq_contratos_numero"), "contratos", ["numero"])
    op.drop_index(op.f("ix_contratos_tipo_instrumento"), table_name="contratos")
    op.drop_column("contratos", "tipo_instrumento")

    op.drop_index("ix_contracts_tipo_numero", table_name="contracts")
    op.drop_index(op.f("ix_contracts_tipo_instrumento"), table_name="contracts")
    op.drop_column("contracts", "tipo_instrumento")
