"""Sprint 2 API regression tests. SQLite fixture, not PostgreSQL concurrency proof."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def test_UC007_UC008_UC010_UC011_booking_payment_notification(client, auth, court_payload):
    owner=auth(); player=auth('player@tests.example.com'); other=auth('owner2@tests.example.com')
    court=client.post('/api/courts',json=court_payload,headers=owner).json()['id']
    start=(datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))+timedelta(days=7)).replace(hour=18,minute=0,second=0,microsecond=0)
    payload={'court_id':court,'start_at':start.isoformat(),'end_at':(start+timedelta(hours=1)).isoformat()}
    r=client.post('/api/bookings',json=payload,headers=player);assert r.status_code==201,r.text
    b=r.json();id=b['id'];assert b['status']=='PENDING' and b['payment_status']=='UNPAID'
    assert client.post('/api/bookings',json=payload,headers=player).status_code==409
    assert client.post(f'/api/bookings/{id}/approve',headers=other).status_code==403
    assert client.post(f'/api/bookings/{id}/approve',headers=owner).json()['status']=='CONFIRMED'
    r=client.post(f'/api/bookings/{id}/payment-submit',headers=player,json={'reference':'DEMO-TEST'});assert r.status_code==200 and r.json()['payment_status']=='SUBMITTED'
    r=client.post(f'/api/bookings/{id}/payment-confirm',headers=owner);assert r.status_code==200 and r.json()['payment_status']=='PAID'
    notices=client.get('/api/notifications',headers=player).json();assert notices
    assert client.post(f"/api/notifications/{notices[0]['id']}/read",headers=other).status_code==404
    assert client.post(f"/api/notifications/{notices[0]['id']}/read",headers=player).json()['read'] is True
    r=client.post(f'/api/bookings/{id}/cancel',headers=player);assert r.status_code==200 and r.json()['status']=='CANCELLED' and r.json()['payment_status']=='REFUND_REVIEW'
    assert client.post('/api/bookings',json=payload,headers=player).status_code==201


def test_UC009_reschedule_releases_original_slot(client, auth, court_payload):
    owner=auth(); player=auth('player@tests.example.com')
    court=client.post('/api/courts',json=court_payload,headers=owner).json()['id']
    start=(datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))+timedelta(days=8)).replace(hour=16,minute=0,second=0,microsecond=0)
    def interval(s):return {'start_at':s.isoformat(),'end_at':(s+timedelta(hours=1)).isoformat()}
    payload={'court_id':court,**interval(start)}
    r=client.post('/api/bookings',headers=player,json=payload);assert r.status_code==201
    id=r.json()['id'];assert client.post(f'/api/bookings/{id}/approve',headers=owner).status_code==200
    r=client.post(f'/api/bookings/{id}/reschedule',headers=player,json=interval(start+timedelta(hours=2)));assert r.status_code==200 and r.json()['status']=='PENDING',r.text
    assert client.post('/api/bookings',headers=player,json=payload).status_code==201
