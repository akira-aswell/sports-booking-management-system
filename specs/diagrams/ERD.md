# Full physical ERD — migrations 0001 and 0002

```mermaid
erDiagram
 USERS ||--o{ COURTS : owns
 SPORTS ||--o{ COURTS : classifies
 COURTS ||--o{ OPERATING_HOURS : opens
 COURTS ||--o{ MAINTENANCE_WINDOWS : closes
 COURTS ||--o{ BOOKINGS : reserved
 USERS ||--o{ BOOKINGS : requests
 BOOKINGS ||--o| PAYMENTS : demo_payment
 USERS ||--o{ NOTIFICATIONS : receives
 COURTS ||--o{ COURT_ALLOCATIONS : occupies
 BOOKINGS o|--o| COURT_ALLOCATIONS : booking_source
 MATCHES o|--o| COURT_ALLOCATIONS : match_source
 USERS ||--o{ TEAMS : captains
 TEAMS ||--o{ TEAM_MEMBERS : includes
 USERS ||--o{ TOURNAMENTS : organizes
 SPORTS ||--o{ TOURNAMENTS : sport
 TOURNAMENTS ||--o{ TOURNAMENT_REGISTRATIONS : accepts
 TEAMS ||--o{ TOURNAMENT_REGISTRATIONS : applies
 TOURNAMENTS ||--o{ MATCHES : contains
 TEAMS ||--o{ MATCHES : home
 TEAMS ||--o{ MATCHES : away
 COURTS o|--o{ MATCHES : scheduled_at
```

The two optional source relationships on COURT_ALLOCATIONS are mutually exclusive: exactly one source must exist. The application creates one payment/allocation for each successful booking; DB relationships alone allow zero dependent rows. A match may have no court before scheduling. Migration 0002 adds nine tables to the five-table foundation; `alembic_version` is metadata, not a business entity.
