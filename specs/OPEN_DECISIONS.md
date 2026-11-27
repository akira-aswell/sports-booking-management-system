# Open decisions and discrepancies

All entries OPEN until agreed; no fake approvals. If actual behavior differs from desired requirements, record a change request, update UC/AC, then modify code/tests.

| ID | Observation / question | Recommended review | Owner |
|---|---|---|---|
| OD-01 | PENDING holds a slot indefinitely in inspected code; no expiry endpoint | Agree whether indefinite hold is acceptable for MVP or add expiry in future | Vũ / Khoa |
| OD-02 | Reschedule validates new future start but not explicitly the original start | Decide if an already-started booking must be blocked from rescheduling; test before fix | Vũ / Hùng |
| OD-03 | Opening-hour and maintenance checks use business end, whereas allocations include buffer | Decide whether buffer must also fit opening/maintenance limits; align availability, booking, match and hour edits | Hùng / Vũ |
| OD-04 | Availability grid advances by 30 minutes; booking duration is validated but no explicit start-grid alignment in service | Decide if off-grid starts are allowed; add AC after decision | Hùng / Vinh |
| OD-05 | Shared allocation prevents court overlaps; team conflict check is within same tournament | Confirm cross-tournament team scheduling policy; not claimed | Tuấn |
| OD-06 | Fullstack main.py and App.tsx import Sprint 3 modules | Choose an explicit Sprint 2 integration branch with reduced routers/routes; no staged file list guarantees runnability | Khánh / Tuấn / Vinh |
| OD-07 | Booking status is independent of payment; no auto-completion or real refund | Confirm scope and do not add invented states to diagrams | Khoa / Vũ |
| OD-08 | Current source checks active court on booking; search also filters active sport | Decide whether inactive sport should prevent direct detail/booking; test expected policy | Khánh / Vũ |
| OD-09 | Team's real repo and runtime not available to this package author | Verify imports, actual revision, route list, test and browser results | Khánh |

Record selected policy, rationale, date and actual approver in REVIEW_LOG.md after discussion. Do not backdate.
