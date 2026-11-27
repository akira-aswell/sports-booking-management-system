# UI specification — draft for Vinh

| Page | Actor | Required UI behavior | UC |
|---|---|---|---|
| /login, /register | Visitor | Validate fields, show server error, store login state; public role selector excludes Admin/Organizer | UC-001/002 |
| / | Public | Filters, loading, error, empty results, court detail link | UC-003 |
| /courts/:id | Public / Player | Detail, date/duration, slot reasons; authenticated eligible actor can submit booking in Sprint 2 | UC-006/007 |
| /owner | Owner/Admin | Create/update courts, hours, maintenance; show server authorization/conflict errors | UC-004/005 |
| /bookings | Player/Admin | Mine list, booking and payment badges separately, applicable cancel/reschedule/payment actions | UC-008/009/010 |
| /owner/bookings | Owner/Admin | Review pending requests, reject/approve, verify submitted demo payments | UC-008/010 |
| /notifications | Authenticated | Private events, mark read, loading/empty/error | UC-011 |
| /teams | Authenticated | Team list and captain roster actions | UC-012 |
| /tournaments, /tournaments/:id | Public / captain | Directory, registration, fixtures and standings | UC-013/014/015 |
| /organizer | Organizer/Admin | Create tournament, decide registrations, generate/schedule/score | UC-013/014/015 |
| /admin | Admin | Catalog and full admin overview/user controls | UC-016/017 |

Do not infer an operation is authorized just because a button is hidden. The backend is the authority. UI behavior above is the acceptance target; detailed screens require a browser run. Do not expose Sprint 3 navigation in a Sprint 2-only integration unless it is clearly disabled or labeled not implemented. Demo payment must be labeled simulated.
