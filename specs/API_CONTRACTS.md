# API contract index

Base `/api`; JSON; protected calls use bearer JWT. Running OpenAPI `/docs` and schemas.py are the detailed payload reference. This index is reconstructed from the prototype; verify against the team's deployed version. Error contract: 401 unauthenticated/invalid login, 403 wrong authorization, 404 missing or hidden resource, 422 invalid input, 409 business/occupancy conflict. Status depends on the individual endpoint.

| Method / route (relative to /api) | Access | Outcome / UC |
|---|---|---|
| POST /auth/register | Public PLAYER/OWNER | 201 token + user; UC-001 |
| POST /auth/login; GET /auth/me | Public login / authenticated me | 200 token or identity; UC-002 |
| GET /sports; GET /sports/admin | Public / admin | catalog; UC-016 |
| POST /sports; PATCH /sports/{sport_id} | Admin | add/update catalog; UC-016 |
| GET /courts; GET /courts/{court_id} | Public | paginated list / detail; UC-003 |
| GET /courts/mine | Owner/Admin | owned courts / all; UC-004 |
| POST /courts; PATCH /courts/{court_id} | Owner/Admin, ownership for patch | 201/200; UC-004 |
| PUT /courts/{court_id}/hours | Owning owner/Admin | replace hours; UC-005 |
| POST /courts/{court_id}/maintenance; DELETE /courts/{court_id}/maintenance/{maintenance_id} | Owning owner/Admin | 201/204; UC-005 |
| GET /courts/{court_id}/availability | Public | date, duration, slots; UC-006 |
| POST /bookings | Player/Admin | 201 PENDING; UC-007 |
| GET /bookings?scope=mine/owner/all | Authenticated mine / Owner+Admin owner / Admin all | list; UC-008 |
| GET /bookings/{booking_id} | Booking player/owning owner/Admin | detail; UC-008 |
| POST /bookings/{booking_id}/approve or /reject | Owning owner/Admin | 200; UC-008 |
| POST /bookings/{booking_id}/cancel | Authorized party/Admin | 200; UC-009 |
| POST /bookings/{booking_id}/reschedule | Booking player/Admin | 200 PENDING; UC-009 |
| POST /bookings/{booking_id}/payment-submit | Booking player/Admin | 200 SUBMITTED; UC-010 |
| POST /bookings/{booking_id}/payment-confirm | Owning owner/Admin | 200 PAID; UC-010 |
| GET /notifications; POST /notifications/{notification_id}/read | Authenticated recipient | 200; UC-011 |
| GET/POST /teams; GET /teams/{team_id} | Authenticated; detail captain/Admin | team list/create/detail; UC-012 |
| POST /teams/{team_id}/members; DELETE /teams/{team_id}/members/{member_id} | Captain/Admin | 200/204; UC-012 |
| GET /tournaments; GET /tournaments/{id}; GET /tournaments/{id}/registrations | Public | directory/detail/entries; UC-013 |
| POST /tournaments; PATCH /tournaments/{id}/status | Organizer/Admin; owning organizer for status | create/change state; UC-013/015 |
| POST /tournaments/{id}/register | Captain/Admin | 201; UC-013 |
| POST /tournaments/{id}/registrations/{registration_id}/approve or /reject | Owning organizer/Admin | 200; UC-013 |
| POST /tournaments/{id}/generate-fixtures; POST /tournaments/{id}/matches/{match_id}/schedule | Owning organizer/Admin | 200; UC-014 |
| GET /tournaments/{id}/matches; GET /tournaments/{id}/standings | Public | fixtures / standings; UC-014/015 |
| POST /tournaments/{id}/matches/{match_id}/score | Owning organizer/Admin | 200; UC-015 |
| GET /admin/overview; GET /admin/users; PATCH /admin/users/{user_id}/active | Admin | 200; UC-017 |

## Sprint 2 payload examples
Choose a future free slot in Vietnam local time; replace the IDs and dates with actual demo values.
```json
{"court_id": 1, "start_at": "2026-12-03T18:00:00+07:00", "end_at": "2026-12-03T19:00:00+07:00", "note": "Demo request"}
```
Reschedule body contains start_at/end_at. Payment-submit body: `{"reference":"DEMO-001"}`. Approve, reject, cancel, payment-confirm and mark-read require no business payload. Return booking includes status, total_amount and payment_status; do not infer payment state from booking status.
