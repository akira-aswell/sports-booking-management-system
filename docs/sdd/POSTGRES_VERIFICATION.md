# PostgreSQL verification runbook — Hùng

Prerequisites: actual integrated Sprint 2 backend, migrations 0001 and 0002, local development seed, PostgreSQL (not SQLite). Confirm DB service and published host port in compose.yaml; Fullstack earlier config commonly maps DB to 5433. Use the credentials in local `.env`, not a real shared database. Do not reset other project volumes.

## 1. Confirm schema
```powershell
docker compose ps
docker compose exec backend alembic current
docker compose exec db psql -U datsan -d datsan -c "SELECT version_num FROM alembic_version;"
```
Adjust database user/name if your env differs. Expected revision 0002_complete. Execute DB_VERIFICATION.sql in DBeaver using the demo database. All invariant exception queries should return zero rows; constraint queries should contain the named checks and GiST exclusion. A zero-row result on an empty DB is not sufficient evidence.

## 2. Verify a free slot and run concurrent requests
Choose an active court whose minimum duration permits 60 minutes, open from 18:00 to 19:00 on a future date. Confirm no maintenance/allocation/buffer conflict. The existing script uses a fixed 18:00–19:00 local interval; `--date` must be a free future date. Import the existing `scripts/verify_pg_concurrency.py` only when reviewed. Example in PowerShell from repo root:
```powershell
py scripts/verify_pg_concurrency.py --base http://127.0.0.1:8000/api --court 1 --workers 50 --date 2026-12-04
```
Replace date, court and API port with actual free values. Demo credentials in the script must match seed; do not share real credentials. The script creates a real booking in the demo database on success.

Expected output: 1 HTTP 201, 49 HTTP 409, one new booking ID. Save the actual console output. Query the matching booking and allocation rows to confirm exactly one active allocation for that interval. Test separate non-overlapping slots and different courts too. Cancel the disposable booking through the authorized endpoint after recording evidence, or use another free slot next time. The script prints a check but does not itself assert via nonzero exit; read the counts.

## 3. Report
Record run date, commit SHA, PostgreSQL version, migration, court/date/interval, counts by HTTP status, returned booking IDs, SQL evidence and reviewer. Link UC-007-AC-03 / TC-007-03. No test was run as part of this documentation package.
