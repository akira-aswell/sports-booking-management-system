import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Sport, User, UserRole
from app.core.security import hash_password


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with session_factory() as db:
        db.add_all([
            User(email="admin@tests.example.com", full_name="Admin", password_hash=hash_password("Secret123!"), role=UserRole.ADMIN),
            User(email="owner@tests.example.com", full_name="Owner", password_hash=hash_password("Secret123!"), role=UserRole.OWNER),
            User(email="owner2@tests.example.com", full_name="Owner2", password_hash=hash_password("Secret123!"), role=UserRole.OWNER),
            User(email="player@tests.example.com", full_name="Player", password_hash=hash_password("Secret123!"), role=UserRole.PLAYER),
            Sport(name="Bóng đá"), Sport(name="Tennis"),
        ])
        db.commit()

    def override_get_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def auth(client):
    def get(email="owner@tests.example.com", password="Secret123!"):
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
    return get


@pytest.fixture
def court_payload():
    return {
        "name": "Sân demo integration test", "sport_id": 1, "address": "123 Phố Vọng, Hà Nội",
        "district": "Hai Bà Trưng", "description": "Sân thử nghiệm", "price_per_hour": "200000.00",
        "min_duration_minutes": 60, "buffer_minutes": 0,
    }
