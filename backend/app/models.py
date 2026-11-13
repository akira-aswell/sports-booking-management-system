from __future__ import annotations

import enum
from datetime import datetime, time, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    PLAYER = "PLAYER"
    OWNER = "OWNER"
    ORGANIZER = "ORGANIZER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.PLAYER)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    courts: Mapped[list[Court]] = relationship(back_populates="owner")


class Sport(Base):
    __tablename__ = "sports"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    courts: Mapped[list[Court]] = relationship(back_populates="sport")


class Court(Base):
    __tablename__ = "courts"
    __table_args__ = (
        CheckConstraint("price_per_hour > 0", name="positive_price"),
        CheckConstraint("min_duration_minutes >= 30", name="min_duration"),
        CheckConstraint("buffer_minutes >= 0", name="nonnegative_buffer"),
        Index("ix_courts_sport_district", "sport_id", "district"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    price_per_hour: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    buffer_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner: Mapped[User] = relationship(back_populates="courts")
    sport: Mapped[Sport] = relationship(back_populates="courts")
    operating_hours: Mapped[list[OperatingHour]] = relationship(
        back_populates="court", cascade="all, delete-orphan", order_by="OperatingHour.weekday"
    )
    maintenance_windows: Mapped[list[MaintenanceWindow]] = relationship(
        back_populates="court", cascade="all, delete-orphan"
    )


class OperatingHour(Base):
    __tablename__ = "operating_hours"
    __table_args__ = (
        UniqueConstraint("court_id", "weekday", name="uq_operating_hours_court_weekday"),
        CheckConstraint("open_time < close_time", name="valid_hours"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.id", ondelete="CASCADE"), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
    court: Mapped[Court] = relationship(back_populates="operating_hours")


class MaintenanceWindow(Base):
    __tablename__ = "maintenance_windows"
    __table_args__ = (CheckConstraint("start_at < end_at", name="valid_maintenance_window"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.id", ondelete="CASCADE"), nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(String(250), nullable=False, default="Bảo trì")
    court: Mapped[Court] = relationship(back_populates="maintenance_windows")

# Sprint 2–3 domain tables. All timestamps are UTC at rest.
class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("start_at < end_at", name="valid_booking_period"),
        CheckConstraint("total_amount >= 0", name="nonnegative_booking_amount"),
        Index("ix_bookings_court_period", "court_id", "start_at", "end_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.id", ondelete="RESTRICT"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    note: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    court: Mapped[Court] = relationship()
    player: Mapped[User] = relationship()


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNPAID")
    method: Mapped[str] = mapped_column(String(30), nullable=False, default="DEMO_TRANSFER")
    reference: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    booking: Mapped[Booking] = relationship()


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    captain_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    captain: Mapped[User] = relationship()
    members: Mapped[list[TeamMember]] = relationship(back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "name", name="uq_team_member_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    jersey_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    team: Mapped[Team] = relationship(back_populates="members")


class Tournament(Base):
    __tablename__ = "tournaments"
    __table_args__ = (CheckConstraint("max_teams >= 2", name="valid_max_teams"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    format: Mapped[str] = mapped_column(String(30), nullable=False, default="ROUND_ROBIN")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    max_teams: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False, default="Hà Nội")
    organizer: Mapped[User] = relationship()
    sport: Mapped[Sport] = relationship()


class TournamentRegistration(Base):
    __tablename__ = "tournament_registrations"
    __table_args__ = (UniqueConstraint("tournament_id", "team_id", name="uq_tournament_team"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    team: Mapped[Team] = relationship()
    tournament: Mapped[Tournament] = relationship()


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("home_team_id <> away_team_id", name="distinct_match_teams"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False, index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    court_id: Mapped[int | None] = mapped_column(ForeignKey("courts.id", ondelete="SET NULL"), nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SCHEDULED")
    home_team: Mapped[Team] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped[Team] = relationship(foreign_keys=[away_team_id])
    court: Mapped[Court | None] = relationship()
    tournament: Mapped[Tournament] = relationship()


class CourtAllocation(Base):
    """One atomic occupancy ledger for bookings and scheduled tournament matches."""
    __tablename__ = "court_allocations"
    __table_args__ = (
        CheckConstraint("start_at < end_at", name="valid_allocation_period"),
        Index("ix_allocations_court_period", "court_id", "start_at", "end_at"),
        CheckConstraint("(booking_id IS NOT NULL) <> (match_id IS NOT NULL)", name="allocation_single_source"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.id", ondelete="RESTRICT"), nullable=False, index=True)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=True)
    match_id: Mapped[int | None] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), unique=True, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
