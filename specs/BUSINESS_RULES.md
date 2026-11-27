# Business rules — draft baseline

| ID | Rule | Related use cases |
|---|---|---|
| RULE-001 | Public registration permits PLAYER and OWNER only; privileged accounts require controlled provisioning. Normalize email; prevent duplicates. | UC-001, UC-002 |
| RULE-002 | Backend validates JWT, active account and role; court and booking ownership are checked independently of UI guards. | UC-002, UC-004, UC-008, UC-009, UC-010 |
| RULE-003 | Discovery lists active courts associated with active sports. Only owner/admin may mutate courts. | UC-003, UC-004 |
| RULE-004 | Weekly hours have one interval per weekday; start precedes end. Maintenance temporarily blocks slots. | UC-005, UC-006 |
| RULE-005 | Booking start/end must include timezone, be future, within same Vietnam-local calendar day, positive and no more than 4 hours; integer-minute duration must meet court minimum and be a multiple of 30. | UC-007, UC-009, UC-014 |
| RULE-006 | Active court, opening hours, maintenance and active allocations must be checked before allocation. Occupancy includes court buffer after end; adjacent half-open intervals without buffer do not overlap. | UC-006, UC-007, UC-009, UC-014 |
| RULE-007 | Creation holds the slot at PENDING, creates UNPAID payment and sends owner notification atomically. PostgreSQL prevents overlapping active allocations for a court. | UC-007 |
| RULE-008 | Only owning owner/admin approve or reject a pending request. Rejection and cancellation release its allocation. | UC-008, UC-009 |
| RULE-009 | Cancellation is allowed for PENDING/CONFIRMED before start by authorized parties. A submitted/paid marker becomes REFUND_REVIEW; no automatic refund. | UC-009 |
| RULE-010 | Reschedule by booking player/admin, only PENDING/CONFIRMED with UNPAID payment; new slot validated, price recalculated, state PENDING and owner notified. Original-start policy is unresolved. | UC-009 |
| RULE-011 | Fee is hourly rate × duration in hours, rounded to two decimal places. Buffer consumes occupancy but is not added to charge. | UC-007, UC-009 |
| RULE-012 | Payment reference may be submitted or replaced by booking player/admin only for CONFIRMED booking with UNPAID/SUBMITTED; owning owner/admin confirms only SUBMITTED. No real payment. | UC-010 |
| RULE-013 | Notifications are private to recipient; marking another user's notification returns 404. | UC-011 |
| RULE-014 | Team captain/admin manages roster; duplicate name (case-insensitive check) refused; app limit 40 members. | UC-012 |
| RULE-015 | Only OPEN tournaments accept pending registration; no duplicate team; pending+approved count against capacity. Organizer/admin reviews pending entries. | UC-013 |
| RULE-016 | Fixtures use approved teams only; one generation while OPEN; round robin pairs each team once, knockout requires power-of-two team count. | UC-014 |
| RULE-017 | Match scheduling checks sport, tournament dates, availability and overlapping teams within the same tournament. Shared allocation guards matches versus bookings. | UC-014 |
| RULE-018 | Knockout scores cannot tie; all matches in round must finish before next round. Round robin standings sort points, goal difference, goals for, name. | UC-015 |
| RULE-019 | Admin can manage catalog and accounts; cannot deactivate current admin account. | UC-016, UC-017 |

These rules describe inspected source behavior. See OPEN_DECISIONS for assumptions and policies requiring approval. IDs are stable; revise the spec and tests when rules change.
