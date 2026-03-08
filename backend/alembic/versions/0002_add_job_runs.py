"""add job_runs table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_runs",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("job_name", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("rows_affected", sa.Integer(), nullable=True),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_job_runs_job_name_started",
        "job_runs",
        ["job_name", "started_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_job_runs_job_name_started", table_name="job_runs")
    op.drop_table("job_runs")
