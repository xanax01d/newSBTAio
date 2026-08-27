"""Initial schema for users, study_groups, schedule_entries, and reports.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=True),
        sa.Column("is_banned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("selected_stage", sa.String(length=16), nullable=True),
        sa.Column("selected_course", sa.Integer(), nullable=True),
        sa.Column("selected_group", sa.String(length=32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "study_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("stage", sa.String(length=16), nullable=False),
        sa.Column("course", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        "ix_study_groups_stage_course",
        "study_groups",
        ["stage", "course"],
    )

    op.create_table(
        "schedule_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("lesson_number", sa.Integer(), nullable=False),
        sa.Column("subgroup", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("time_range", sa.String(length=32), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("auditorium", sa.String(length=64), nullable=True),
        sa.Column("teacher", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["study_groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "group_id",
            "week_number",
            "day_of_week",
            "lesson_number",
            "subgroup",
            name="uq_schedule_slot",
        ),
    )
    op.create_index(
        "ix_schedule_lookup",
        "schedule_entries",
        ["group_id", "week_number", "day_of_week"],
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("group_name", sa.String(length=32), nullable=False),
        sa.Column("day_name", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reports_user_id", "reports", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_reports_user_id", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_schedule_lookup", table_name="schedule_entries")
    op.drop_table("schedule_entries")
    op.drop_index("ix_study_groups_stage_course", table_name="study_groups")
    op.drop_table("study_groups")
    op.drop_table("users")
