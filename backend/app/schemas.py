from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models import UserRole


class PublicRole(str, Enum):
    PLAYER = "PLAYER"
    OWNER = "OWNER"


class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: PublicRole = PublicRole.PLAYER


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    role: UserRole


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SportIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    active: bool = True


class SportPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    active: bool | None = None


class SportOut(SportIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourtBase(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    sport_id: int = Field(gt=0)
    address: str = Field(min_length=5, max_length=300)
    district: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=2000)
    price_per_hour: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    min_duration_minutes: int = Field(default=60, ge=30, le=240, multiple_of=30)
    buffer_minutes: int = Field(default=0, ge=0, le=120, multiple_of=30)
    active: bool = True


class CourtCreate(CourtBase):
    pass


class CourtPatch(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=160)
    sport_id: int | None = Field(default=None, gt=0)
    address: str | None = Field(default=None, min_length=5, max_length=300)
    district: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    price_per_hour: Decimal | None = Field(default=None, gt=0)
    min_duration_minutes: int | None = Field(default=None, ge=30, le=240, multiple_of=30)
    buffer_minutes: int | None = Field(default=None, ge=0, le=120, multiple_of=30)
    active: bool | None = None


class OperatingHourIn(BaseModel):
    weekday: int = Field(ge=0, le=6)
    open_time: time
    close_time: time

    @model_validator(mode="after")
    def check_order(self):
        if self.open_time >= self.close_time:
            raise ValueError("Giờ đóng cửa phải sau giờ mở cửa")
        return self


class OperatingHourOut(OperatingHourIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MaintenanceIn(BaseModel):
    start_at: datetime
    end_at: datetime
    reason: str = Field(default="Bảo trì", min_length=2, max_length=250)

    @model_validator(mode="after")
    def check_order(self):
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValueError("Thời gian phải có timezone, ví dụ +07:00")
        if self.start_at >= self.end_at:
            raise ValueError("Thời gian kết thúc phải sau bắt đầu")
        return self


class MaintenanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    start_at: datetime
    end_at: datetime
    reason: str

    @field_validator("start_at", "end_at", mode="before")
    @classmethod
    def force_utc_if_missing_tz(cls, value):
        # SQLite used by unit tests does not preserve timezone; PostgreSQL does.
        from datetime import timezone
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class CourtOut(CourtBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    sport: SportOut


class CourtDetailOut(CourtOut):
    operating_hours: list[OperatingHourOut]
    maintenance_windows: list[MaintenanceOut]


class CourtListOut(BaseModel):
    items: list[CourtOut]
    total: int


class SlotOut(BaseModel):
    start_at: datetime
    end_at: datetime
    available: bool
    reason: str | None = None


class AvailabilityOut(BaseModel):
    court_id: int
    date: date
    duration_minutes: int
    note: str = "Lịch thực tế gồm giờ mở cửa, bảo trì, đơn đặt sân và lịch thi đấu."
    slots: list[SlotOut]

# Sprint 2–3 API contracts
class BookingIn(BaseModel):
    court_id: int = Field(gt=0)
    start_at: datetime
    end_at: datetime
    note: str = Field(default='', max_length=500)

class RescheduleIn(BaseModel):
    start_at: datetime
    end_at: datetime

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    court_id: int
    player_id: int
    start_at: datetime
    end_at: datetime
    status: str
    total_amount: Decimal
    note: str
    created_at: datetime
    court_name: str
    player_name: str
    payment_status: str

class PaymentSubmitIn(BaseModel):
    reference: str = Field(min_length=3, max_length=100)

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    message: str
    read: bool
    created_at: datetime

class TeamIn(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str = Field(default='', max_length=500)

class MemberIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    jersey_number: int | None = Field(default=None, ge=0, le=99)

class MemberOut(MemberIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class TeamOut(TeamIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    captain_id: int
    captain_name: str
    members: list[MemberOut] = []

class TournamentIn(BaseModel):
    name: str = Field(min_length=4, max_length=180)
    description: str = Field(default='', max_length=2000)
    sport_id: int = Field(gt=0)
    format: str = Field(default='ROUND_ROBIN', pattern='^(ROUND_ROBIN|KNOCKOUT)$')
    max_teams: int = Field(default=8, ge=2, le=32)
    starts_at: datetime
    ends_at: datetime
    location: str = Field(default='Hà Nội', min_length=2, max_length=200)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None or self.starts_at >= self.ends_at:
            raise ValueError('Cần thời gian bắt đầu/kết thúc có múi giờ, theo đúng thứ tự')
        return self

class TournamentPatch(BaseModel):
    status: str = Field(pattern='^(OPEN|IN_PROGRESS|COMPLETED|CANCELLED)$')

class TournamentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    sport_id: int
    name: str
    description: str
    format: str
    status: str
    max_teams: int
    starts_at: datetime
    ends_at: datetime
    location: str
    sport_name: str
    organizer_name: str
    approved_teams: int = 0

class RegistrationIn(BaseModel):
    team_id: int = Field(gt=0)

class RegistrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tournament_id: int
    team_id: int
    team_name: str
    status: str

class MatchScheduleIn(BaseModel):
    court_id: int = Field(gt=0)
    start_at: datetime
    end_at: datetime

class ScoreIn(BaseModel):
    home_score: int = Field(ge=0, le=99)
    away_score: int = Field(ge=0, le=99)

class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tournament_id: int
    home_team_id: int
    away_team_id: int
    home_team_name: str
    away_team_name: str
    round_number: int
    court_id: int | None
    court_name: str | None
    start_at: datetime | None
    end_at: datetime | None
    home_score: int | None
    away_score: int | None
    status: str

class StandingOut(BaseModel):
    team_id: int
    team_name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

class AdminUserOut(UserOut):
    active: bool

class UserActiveIn(BaseModel):
    active: bool
