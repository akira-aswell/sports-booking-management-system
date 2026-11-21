from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def test_health_and_registration_cannot_escalate_role(client):
    assert client.get("/api/health").json()["status"] == "ok"
    response = client.post("/api/auth/register", json={
        "full_name": "Người mới", "email": "new@tests.example.com", "password": "TestPass123!", "role": "ADMIN"
    })
    assert response.status_code == 422
    response = client.post("/api/auth/register", json={
        "full_name": "Người mới", "email": "new@tests.example.com", "password": "TestPass123!", "role": "PLAYER"
    })
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "PLAYER"
    assert client.post("/api/auth/register", json={
        "full_name": "Người khác", "email": "new@tests.example.com", "password": "TestPass123!", "role": "PLAYER"
    }).status_code == 409


def test_auth_and_admin_sport_access(client, auth):
    assert client.get("/api/auth/me").status_code == 401
    player = auth("player@tests.example.com")
    assert client.get("/api/auth/me", headers=player).json()["role"] == "PLAYER"
    assert client.post("/api/sports", json={"name": "Pickleball"}, headers=player).status_code == 403
    assert client.post("/api/sports", json={"name": "Pickleball"}).status_code == 401
    admin = auth("admin@tests.example.com")
    r = client.post("/api/sports", json={"name": "Pickleball"}, headers=admin)
    assert r.status_code == 201
    assert r.json()["name"] == "Pickleball"
    assert len(client.get("/api/sports").json()) == 3


def test_owner_court_permissions_and_search(client, auth, court_payload):
    assert client.post("/api/courts", json=court_payload, headers=auth("player@tests.example.com")).status_code == 403
    owner = auth()
    r = client.post("/api/courts", json=court_payload, headers=owner)
    assert r.status_code == 201, r.text
    court = r.json()
    assert len(court["operating_hours"]) == 7
    assert client.get("/api/courts?q=demo&district=Bà%20Trưng&sport_id=1").json()["total"] == 1
    assert client.get("/api/courts?max_price=100000").json()["total"] == 0
    assert client.get("/api/courts?sport_id=2").json()["total"] == 0
    assert client.patch(f"/api/courts/{court['id']}", json={"name": "Cố sửa sân"}, headers=auth("owner2@tests.example.com")).status_code == 403
    r = client.patch(f"/api/courts/{court['id']}", json={"price_per_hour": "180000.00"}, headers=owner)
    assert r.status_code == 200
    assert float(r.json()["price_per_hour"]) == 180000
    assert len(client.get("/api/courts/mine", headers=owner).json()) == 1


def test_hour_validation_and_maintenance_slot(client, auth, court_payload):
    token = auth()
    court_id = client.post("/api/courts", json=court_payload, headers=token).json()["id"]
    assert client.put(f"/api/courts/{court_id}/hours", headers=token, json=[
        {"weekday": 0, "open_time": "10:00:00", "close_time": "09:00:00"}
    ]).status_code == 422
    assert client.put(f"/api/courts/{court_id}/hours", headers=token, json=[
        {"weekday": 0, "open_time": "09:00:00", "close_time": "18:00:00"},
        {"weekday": 0, "open_time": "09:00:00", "close_time": "18:00:00"}
    ]).status_code == 422
    # Ensure replacing pre-existing weekday rows works twice (no UNIQUE conflict).
    new_hours = [{"weekday": i, "open_time": "08:00:00", "close_time": "22:00:00"} for i in range(7)]
    assert client.put(f"/api/courts/{court_id}/hours", headers=token, json=new_hours).status_code == 200
    assert client.put(f"/api/courts/{court_id}/hours", headers=token, json=new_hours).status_code == 200

    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    date = (datetime.now(tz) + timedelta(days=7)).date()
    start = datetime.combine(date, datetime.min.time(), tzinfo=tz).replace(hour=9)
    end = start + timedelta(hours=1)
    r = client.post(f"/api/courts/{court_id}/maintenance", headers=token, json={
        "start_at": start.isoformat(), "end_at": end.isoformat(), "reason": "Test bảo trì"
    })
    assert r.status_code == 201, r.text
    maintenance_id = r.json()["id"]
    r = client.get(f"/api/courts/{court_id}/availability", params={"date": date.isoformat()})
    assert r.status_code == 200, r.text
    slots = r.json()["slots"]
    blocked = [s for s in slots if s["reason"] == "Bảo trì / Tạm đóng"]
    assert blocked
    assert any(s["available"] for s in slots)
    assert "đơn đặt sân" in r.json()["note"]
    assert client.delete(f"/api/courts/{court_id}/maintenance/{maintenance_id}", headers=token).status_code == 204
