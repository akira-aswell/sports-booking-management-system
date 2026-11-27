# Project scope and stakeholders

DatSan is an educational sports-facility discovery, reservation and amateur tournament application. The local deployment uses React/TypeScript, FastAPI, SQLAlchemy, PostgreSQL and Docker Compose. Payments are simulated; sample data is fictional. The project does not claim production readiness.

| Actor | Goal |
|---|---|
| Visitor | Search and inspect courts and public tournaments |
| Player | Reserve courts, manage own bookings, manage teams |
| Owner | Maintain owned facilities and review bookings |
| Organizer | Manage amateur competitions |
| Admin | Maintain catalog and user access |

## Sprint boundaries
- Sprint 1: account, catalog, search, court management, weekly hours and maintenance. Availability is based on these inputs in the standalone Sprint 1 demo.
- Sprint 2: reservations, shared allocation, manual payment markers and in-app notifications; availability also uses allocations. Migration 0002 introduces tables for both Sprint 2 and 3; the presence of tournament tables is not tournament acceptance.
- Sprint 3: teams, registration, round-robin/knockout fixtures, court assignment, scores, standings, admin overview and user controls.

## Success criteria (proposed, not measured)
All in-scope ACs reviewed, each linked to a test case, critical API and browser flows passing on a clean local stack, PostgreSQL concurrent collision protection demonstrated, known gaps recorded. No real payment processing or unsupported tournament formats.

## Status model
Source-inspected = behavior was read in the personal prototype. Reported imported = team reports the file was pushed. Integrated = verified in the team repository, not inferred from file presence. Accepted = reviewed spec and executed passing evidence. These are different states.
