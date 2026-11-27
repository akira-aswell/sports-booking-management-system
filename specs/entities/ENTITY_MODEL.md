# Domain entity model

A domain model explains business concepts before storage details. The physical schema is documented in [database design](../../docs/sdd/DATABASE_DESIGN.md). All proposed ownership assignments are subject to team review.

| Entity | Business meaning | Relationships / lifecycle | Sprint |
|---|---|---|---|
| User | Account with identity and role | Owner of courts; booking party; captain; organizer; notification recipient | 1 |
| Sport | Supported activity category | Classifies courts and tournaments | 1 |
| Court | Rentable facility with price and scheduling policy | One owner and one sport; hours, maintenance and allocations | 1 |
| OperatingHour | Weekly local opening interval | Belongs to a court, unique weekday | 1 |
| MaintenanceWindow | Temporary closure | Belongs to a court; time interval | 1 |
| Booking | Request by a player for a court interval | PENDING, CONFIRMED, REJECTED, CANCELLED are observed transitions | 2 |
| Payment | One simulated payment record per booking | UNPAID, SUBMITTED, PAID, REFUND_REVIEW | 2 |
| Notification | Private in-app event for a user | Unread/read | 2 |
| CourtAllocation | Resource occupancy, not a separate customer order | Exactly one Booking or Match; active flag; end includes buffer | 2 |
| Team | Roster managed by a captain | Members and tournament registrations | 3 |
| TeamMember | Named member of a roster | Belongs to team; not necessarily a User account | 3 |
| Tournament | Competition with sport, time period, format and organizer | OPEN, IN_PROGRESS, COMPLETED, CANCELLED | 3 |
| TournamentRegistration | Team's application to a tournament | PENDING, APPROVED, REJECTED | 3 |
| Match | Fixture between two distinct teams | PLANNED, SCHEDULED, FINISHED, CANCELLED | 3 |

CourtAllocation is shared across the booking and tournament contexts. Do not model payment state as a booking state. A notification is not proof of actual money transfer or external message delivery. Tournament tables already appear in migration 0002; this does not imply the Sprint 3 workflows have been integrated.
