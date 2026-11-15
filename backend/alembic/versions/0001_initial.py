"""Sprint 1: users, sports, courts, operating hours, maintenance.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

role_enum = sa.Enum("PLAYER", "OWNER", "ORGANIZER", "ADMIN", name="user_role")


def upgrade():
    bind = op.get_bind()
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table(
        "sports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("name", name="uq_sports_name"),
    )
    op.create_table(
        "courts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sport_id", sa.Integer(), sa.ForeignKey("sports.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("address", sa.String(300), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price_per_hour", sa.Numeric(12, 2), nullable=False),
        sa.Column("min_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("buffer_minutes", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.CheckConstraint("price_per_hour > 0", name="ck_courts_positive_price"),
        sa.CheckConstraint("min_duration_minutes >= 30", name="ck_courts_min_duration"),
        sa.CheckConstraint("buffer_minutes >= 0", name="ck_courts_nonnegative_buffer"),
    )
    op.create_index("ix_courts_owner_id", "courts", ["owner_id"])
    op.create_index("ix_courts_sport_id", "courts", ["sport_id"])
    op.create_index("ix_courts_district", "courts", ["district"])
    op.create_index("ix_courts_sport_district", "courts", ["sport_id", "district"])
    op.create_table(
        "operating_hours",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("court_id", sa.Integer(), sa.ForeignKey("courts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("open_time", sa.Time(), nullable=False),
        sa.Column("close_time", sa.Time(), nullable=False),
        sa.UniqueConstraint("court_id", "weekday", name="uq_operating_hours_court_weekday"),
        sa.CheckConstraint("open_time < close_time", name="ck_operating_hours_valid_hours"),
    )
    op.create_table(
        "maintenance_windows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("court_id", sa.Integer(), sa.ForeignKey("courts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(250), nullable=False),
        sa.CheckConstraint("start_at < end_at", name="ck_maintenance_windows_valid_maintenance_window"),
    )
    op.create_index("ix_maintenance_windows_court_id", "maintenance_windows", ["court_id"])


def downgrade():
    op.drop_index("ix_maintenance_windows_court_id", table_name="maintenance_windows")
    op.drop_table("maintenance_windows")
    op.drop_table("operating_hours")
    for name in ["ix_courts_sport_district", "ix_courts_district", "ix_courts_sport_id", "ix_courts_owner_id"]:
        op.drop_index(name, table_name="courts")
    op.drop_table("courts")
    op.drop_table("sports")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    role_enum.drop(op.get_bind(), checkfirst=True)
