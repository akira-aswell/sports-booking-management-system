# Database rules and invariants — Hùng

| ID | Invariant | Enforcement / evidence target |
|---|---|---|
| DB-01 | Unique email and sport name; valid references among users, sports and courts | Initial schema, ORM, API tests UC-001/004/016 |
| DB-02 | Court prices and opening hours valid; one weekly interval per court/weekday | Initial migration/validation; UC-004/005 |
| DB-03 | Booking and allocation start precede end; booking amount nonnegative | 0002_complete check constraints |
| DB-04 | Each payment refers to one booking; no second payment row for same booking | Unique payments.booking_id and FK |
| DB-05 | Allocation has exactly one non-null booking_id or match_id; each reference unique | ck_allocation_single_source, UNIQUE keys |
| DB-06 | For same court no active half-open allocation overlaps | PostgreSQL btree_gist, no_active_allocation_overlap |
| DB-07 | Allocation end = business end + buffer; fee excludes buffer | Scheduling service and booking/match API; application invariant |
| DB-08 | Reject/cancel deactivate allocation; booking, payment, allocation and notification updates are transactional | Booking service and transaction tests |
| DB-09 | Time comparisons normalized to UTC; weekly hours use Asia/Ho_Chi_Minh | scheduling.utc, check_interval and availability |
| DB-10 | Team registration unique by tournament/team; two match teams distinct | 0002_complete unique/check constraints |

## Concurrency strategy
1. Obtain a PostgreSQL row lock on the court; expire cached hours/maintenance.
2. Check the requested interval against business rules and active occupancy.
3. Insert/update allocation in the same transaction as booking or match.
4. PostgreSQL exclusion constraint rejects overlaps at DB level even if an application precheck races; return 409 and roll back.

Do not rely on SQLite for the PostgreSQL guarantee. SQLite tests are useful for sequential API behavior but the migration only installs the exclusion constraint on PostgreSQL.

## Known gaps to review
Status values are application strings, not verified as database enum/check constraints in 0002. The DB does not enforce consistency between allocation court and referenced booking/match court by a composite FK. Application logic and regression tests should protect that relationship; propose DB hardening only after team approval. Never edit an already-applied revision solely to hide history; create a new migration if an approved schema change is needed.

## Evidence
Use [read-only SQL checks](../docs/sdd/DB_VERIFICATION.sql) and the [PostgreSQL concurrency runbook](../docs/sdd/POSTGRES_VERIFICATION.md). No live DB results are included.
