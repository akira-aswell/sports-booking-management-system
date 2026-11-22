"""Sprint 2 & 3: reservations, demo payments, notifications, teams, tournaments, matches and occupancy."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_complete"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("bookings",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("court_id",sa.Integer(),sa.ForeignKey("courts.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("player_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("start_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("end_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("status",sa.String(20),nullable=False),
        sa.Column("total_amount",sa.Numeric(12,2),nullable=False),
        sa.Column("note",sa.String(500),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("start_at < end_at",name="ck_bookings_valid_booking_period"),
        sa.CheckConstraint("total_amount >= 0",name="ck_bookings_nonnegative_booking_amount"))
    op.create_index("ix_bookings_court_id","bookings",["court_id"])
    op.create_index("ix_bookings_player_id","bookings",["player_id"])
    op.create_index("ix_bookings_status","bookings",["status"])
    op.create_index("ix_bookings_court_period","bookings",["court_id","start_at","end_at"])
    op.create_table("payments",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("booking_id",sa.Integer(),sa.ForeignKey("bookings.id",ondelete="CASCADE"),nullable=False,unique=True),
        sa.Column("amount",sa.Numeric(12,2),nullable=False),
        sa.Column("status",sa.String(20),nullable=False),
        sa.Column("method",sa.String(30),nullable=False),
        sa.Column("reference",sa.String(100),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("notifications",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("title",sa.String(150),nullable=False),
        sa.Column("message",sa.String(1000),nullable=False),
        sa.Column("read",sa.Boolean(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_notifications_user_id","notifications",["user_id"])
    op.create_table("teams",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("captain_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("name",sa.String(150),nullable=False),
        sa.Column("description",sa.String(500),nullable=False))
    op.create_index("ix_teams_captain_id","teams",["captain_id"])
    op.create_table("team_members",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("team_id",sa.Integer(),sa.ForeignKey("teams.id",ondelete="CASCADE"),nullable=False),
        sa.Column("name",sa.String(120),nullable=False),
        sa.Column("jersey_number",sa.Integer(),nullable=True),
        sa.UniqueConstraint("team_id","name",name="uq_team_member_name"))
    op.create_index("ix_team_members_team_id","team_members",["team_id"])
    op.create_table("tournaments",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("organizer_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("sport_id",sa.Integer(),sa.ForeignKey("sports.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("name",sa.String(180),nullable=False),
        sa.Column("description",sa.Text(),nullable=False),
        sa.Column("format",sa.String(30),nullable=False),
        sa.Column("status",sa.String(30),nullable=False),
        sa.Column("max_teams",sa.Integer(),nullable=False),
        sa.Column("starts_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("ends_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("location",sa.String(200),nullable=False),
        sa.CheckConstraint("max_teams >= 2", name="ck_tournaments_valid_max_teams"))
    op.create_table("tournament_registrations",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tournament_id",sa.Integer(),sa.ForeignKey("tournaments.id",ondelete="CASCADE"),nullable=False),
        sa.Column("team_id",sa.Integer(),sa.ForeignKey("teams.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("status",sa.String(20),nullable=False),
        sa.UniqueConstraint("tournament_id","team_id",name="uq_tournament_team"))
    op.create_index("ix_tournament_registrations_tournament_id","tournament_registrations",["tournament_id"])
    op.create_index("ix_tournament_registrations_team_id","tournament_registrations",["team_id"])
    op.create_table("matches",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("tournament_id",sa.Integer(),sa.ForeignKey("tournaments.id",ondelete="CASCADE"),nullable=False),
        sa.Column("home_team_id",sa.Integer(),sa.ForeignKey("teams.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("away_team_id",sa.Integer(),sa.ForeignKey("teams.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("round_number",sa.Integer(),nullable=False),
        sa.Column("court_id",sa.Integer(),sa.ForeignKey("courts.id",ondelete="SET NULL"),nullable=True),
        sa.Column("start_at",sa.DateTime(timezone=True),nullable=True),
        sa.Column("end_at",sa.DateTime(timezone=True),nullable=True),
        sa.Column("home_score",sa.Integer(),nullable=True),
        sa.Column("away_score",sa.Integer(),nullable=True),
        sa.Column("status",sa.String(20),nullable=False),
        sa.CheckConstraint("home_team_id <> away_team_id", name="ck_matches_distinct_match_teams"))
    op.create_index("ix_matches_tournament_id","matches",["tournament_id"])
    op.create_table("court_allocations",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("court_id",sa.Integer(),sa.ForeignKey("courts.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("booking_id",sa.Integer(),sa.ForeignKey("bookings.id",ondelete="CASCADE"),unique=True,nullable=True),
        sa.Column("match_id",sa.Integer(),sa.ForeignKey("matches.id",ondelete="CASCADE"),unique=True,nullable=True),
        sa.Column("start_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("end_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("active",sa.Boolean(),nullable=False),
        sa.CheckConstraint("start_at < end_at",name="ck_court_allocations_valid_allocation_period"),
        sa.CheckConstraint("(booking_id IS NOT NULL) <> (match_id IS NOT NULL)",name="ck_allocation_single_source"))
    op.create_index("ix_court_allocations_court_id","court_allocations",["court_id"])
    op.create_index("ix_allocations_court_period","court_allocations",["court_id","start_at","end_at"])
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
        op.execute("""ALTER TABLE court_allocations ADD CONSTRAINT no_active_allocation_overlap
            EXCLUDE USING gist (court_id WITH =, tstzrange(start_at,end_at,'[)') WITH &&)
            WHERE (active)""")


def downgrade():
    for table in ["court_allocations","matches","tournament_registrations","tournaments","team_members","teams","notifications","payments","bookings"]:
        op.drop_table(table)
