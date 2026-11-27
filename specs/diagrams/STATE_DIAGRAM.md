# State machines

## Booking (Sprint 2)
```mermaid
stateDiagram-v2
 [*] --> PENDING: create / allocate
 PENDING --> CONFIRMED: owner approves
 PENDING --> REJECTED: owner rejects / release
 PENDING --> CANCELLED: eligible cancellation / release
 CONFIRMED --> CANCELLED: eligible cancellation / release
 PENDING --> PENDING: unpaid reschedule
 CONFIRMED --> PENDING: unpaid reschedule / reapprove
```
No automated COMPLETED or expiry transition is implemented in the inspected booking router. A past booking may retain CONFIRMED. Rejected/cancelled cannot be changed through the inspected action endpoints.

## Payment (separate machine)
```mermaid
stateDiagram-v2
 [*] --> UNPAID: booking created
 UNPAID --> SUBMITTED: confirmed booking reference
 SUBMITTED --> SUBMITTED: replace reference
 SUBMITTED --> PAID: owner verifies demo reference
 SUBMITTED --> REFUND_REVIEW: cancel booking
 PAID --> REFUND_REVIEW: cancel booking
```
Cancellation of an unpaid booking leaves payment UNPAID. PAID is simulation only.

## Tournament (Sprint 3 scope)
```mermaid
stateDiagram-v2
 [*] --> OPEN: create
 OPEN --> IN_PROGRESS: generate fixtures
 IN_PROGRESS --> COMPLETED: finish all RR matches or knockout final
 OPEN --> CANCELLED: cancel
 IN_PROGRESS --> CANCELLED: cancel / release allocations
```
Registration: PENDING → APPROVED or REJECTED. Match: PLANNED → SCHEDULED → FINISHED; a scheduled match may be rescheduled; unfinished matches become CANCELLED when tournament is cancelled. Finished allocations are not explicitly released by scoring; the occupied time range remains recorded. The tournament status API also has a guarded manual COMPLETED request; review that path and the cancellation policy before acceptance.
