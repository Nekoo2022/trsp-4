"""Добавление not null поля description в products.

Revision ID: 20250401_2
Revises: 20250401_1
Create Date: 2026-05-04

У существующих строк поле заполняется пустой строкой через server_default.

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250401_2"
down_revision: Union[str, None] = "20250401_1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "description",
            sa.String(length=2000),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "description")
