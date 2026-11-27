# Reservation creation sequence — UC-007

```mermaid
sequenceDiagram
 actor Player
 participant UI as React
 participant API as FastAPI
 participant S as Scheduling service
 participant DB as PostgreSQL
 Player->>UI: Select court and interval
 UI->>API: POST /api/bookings + JWT
 API->>API: Authorize role and validate payload
 API->>DB: Lock court row
 API->>S: Check interval and compute fee
 S->>DB: Read hours, maintenance, allocations
 alt Invalid or occupied interval
 S-->>API: 422 or 409
 API-->>UI: Error; no booking
 else Valid interval
 API->>DB: Write booking, allocation, payment, notification
 alt Constraint conflict
 DB-->>API: Integrity error
 API->>DB: Roll back
 API-->>UI: 409 Conflict
 else Commit succeeds
 DB-->>API: Committed
 API-->>UI: 201 PENDING, UNPAID
 end
 end
```
Availability is advisory; the booking transaction rechecks the conditions. UI must not announce success before HTTP 201.
