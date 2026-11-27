# Physical database design — Hùng

This is the additive technical companion to the domain entity model. Preserve the existing docs/ERD_FULL.md if present; compare rather than overwrite. For full diagram see ../../specs/diagrams/ERD.md.

| Table | Key columns and relations | Notes |
|---|---|---|
| users | id PK; email, role, active | unique email; password hash |
| sports | id PK; name, active | unique catalog name |
| courts | id PK; owner_id → users; sport_id → sports | price, min_duration_minutes, buffer_minutes, active |
| operating_hours | id PK; court_id → courts; weekday | open_time, close_time, unique court/weekday |
| maintenance_windows | id PK; court_id → courts | start_at, end_at, reason |
| bookings | id PK; court_id → courts; player_id → users | start_at/end_at, status, total_amount NUMERIC(12,2), note, created_at |
| payments | id PK; booking_id unique FK → bookings | amount, status, method, reference, updated_at |
| notifications | id PK; user_id → users | title, message, read, created_at |
| teams | id PK; captain_id → users | name, description |
| team_members | id PK; team_id → teams | name, jersey_number optional; unique team/name |
| tournaments | id PK; organizer_id → users; sport_id → sports | format, status, max_teams, starts_at/ends_at, location |
| tournament_registrations | id PK; tournament_id → tournaments; team_id → teams | status; unique tournament/team |
| matches | id PK; tournament_id → tournaments; home/away_team_id → teams; court_id optional → courts | round_number, optional times/scores, status |
| court_allocations | id PK; court_id → courts; booking_id unique nullable FK; match_id unique nullable FK | active, start_at/end_at, XOR source constraint |

## Migration strategy
- `0001_initial`: foundation (5 business tables).
- `0002_complete`: nine additional tables, including tournament dependencies. In PostgreSQL it installs `btree_gist` and the exclusion constraint for active allocations. Never split or rename a revision already applied to a shared database without an explicit migration plan.
- `alembic_version`: framework metadata; validate current/head and run a clean migration on a disposable volume.

## Why allocation is separate from booking
A booking and a match may both consume the same physical resource. A single occupancy table prevents separate booking/match constraints from missing cross-module collisions. The allocation interval stores the buffer after the business interval. The `[)` range permits adjacent intervals when no buffer is required. Inactive allocations preserve history without blocking new slots. Transaction locks coordinate schedule edits and allocations; exclusion is the last-line DB guarantee.

## Verification targets
Review FK direction and delete policy in migration, validate active overlap query returns no rows, confirm XOR and exclusion constraints on PostgreSQL, run concurrent booking test on a fresh free slot. Check payment and booking consistency, including failed reschedule. Source references: backend/app/models.py, backend/alembic/versions/0002_complete.py, backend/app/services/scheduling.py, backend/app/api/bookings.py and courts.py. All runtime checks pending.
