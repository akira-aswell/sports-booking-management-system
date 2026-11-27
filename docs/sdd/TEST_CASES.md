# Acceptance test catalog

Execution protocol: use an isolated demo DB, create known fixtures, capture actual HTTP status and JSON/DB evidence, restore or remove disposable test data. Never record PASS before execution. The source test suite uses SQLite fixtures; PostgreSQL-specific checks require PostgreSQL.

## UC-001 — Register account

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-001-01 | UC-001-AC-01 | New valid PLAYER | Register | 201 and PLAYER identity | backend/tests/test_sprint1.py::test_health_and_registration_cannot_escalate_role | NOT RUN |
| TC-001-02 | UC-001-AC-02 | Existing email | Register again | 409; no duplicate | backend/tests/test_sprint1.py::test_health_and_registration_cannot_escalate_role | NOT RUN |
| TC-001-03 | UC-001-AC-03 | Requested ADMIN role | Register | 422; no privileged account | backend/tests/test_sprint1.py::test_health_and_registration_cannot_escalate_role | NOT RUN |
| TC-001-04 | UC-001-AC-04 | Valid OWNER | Register | 201 and OWNER identity | New test required; not executed | NOT RUN |

## UC-002 — Authenticate and authorize

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-002-01 | UC-002-AC-01 | Valid player | Login then GET /api/auth/me | 200 and PLAYER role | backend/tests/test_sprint1.py::test_auth_and_admin_sport_access (fixture logs in) | NOT RUN |
| TC-002-02 | UC-002-AC-02 | No token | GET /api/auth/me | 401 | backend/tests/test_sprint1.py::test_auth_and_admin_sport_access | NOT RUN |
| TC-002-03 | UC-002-AC-03 | Player token | POST /api/sports | 403 | backend/tests/test_sprint1.py::test_auth_and_admin_sport_access | NOT RUN |
| TC-002-04 | UC-002-AC-04 | Invalid password or disabled account | Login | 401 | New test required; not executed | NOT RUN |

## UC-003 — Search and inspect courts

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-003-01 | UC-003-AC-01 | Matching active court | Apply keyword/district/sport filters | Correct court and total returned | backend/tests/test_sprint1.py::test_owner_court_permissions_and_search | NOT RUN |
| TC-003-02 | UC-003-AC-02 | Court above maximum price | Filter | Not returned | backend/tests/test_sprint1.py::test_owner_court_permissions_and_search | NOT RUN |
| TC-003-03 | UC-003-AC-03 | Minimum price exceeds maximum | Search | 422 | New test required; not executed | NOT RUN |
| TC-003-04 | UC-003-AC-04 | Inactive court or sport | Search | Excluded from list | New test required; not executed | NOT RUN |

## UC-004 — Manage courts

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-004-01 | UC-004-AC-01 | Owner and valid sport | Create court | 201; seven initial opening-hour rows | backend/tests/test_sprint1.py::test_owner_court_permissions_and_search | NOT RUN |
| TC-004-02 | UC-004-AC-02 | Player or different owner | Create / modify another owner court | 403 | backend/tests/test_sprint1.py::test_owner_court_permissions_and_search | NOT RUN |
| TC-004-03 | UC-004-AC-03 | Own court | Change price | 200 and updated amount | backend/tests/test_sprint1.py::test_owner_court_permissions_and_search | NOT RUN |
| TC-004-04 | UC-004-AC-04 | Inactive sport or invalid input | Create court | 422; no court created | New test required; not executed | NOT RUN |

## UC-005 — Manage opening hours and maintenance

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-005-01 | UC-005-AC-01 | Repeated weekday or closing before opening | Replace hours | 422 | backend/tests/test_sprint1.py::test_hour_validation_and_maintenance_slot | NOT RUN |
| TC-005-02 | UC-005-AC-02 | Valid hours | Replace twice | 200 both times without duplicate weekday | backend/tests/test_sprint1.py::test_hour_validation_and_maintenance_slot | NOT RUN |
| TC-005-03 | UC-005-AC-03 | Future maintenance | Create and inspect availability | 201; affected slots blocked; delete 204 | backend/tests/test_sprint1.py::test_hour_validation_and_maintenance_slot | NOT RUN |
| TC-005-04 | UC-005-AC-04 | Existing active allocation (Sprint 2) | Create overlapping maintenance | 409; allocation preserved | backend/tests/test_fullstack.py::test_permissions_admin_and_maintenance | NOT RUN |
| TC-005-05 | UC-005-AC-05 | Existing future allocation (Sprint 2) | Replace hours excluding it | 409; previous hours preserved | New test required; not executed | NOT RUN |

## UC-006 — Check court availability

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-006-01 | UC-006-AC-01 | Maintenance interval | Query date | Blocked slots plus other available slots | backend/tests/test_sprint1.py::test_hour_validation_and_maintenance_slot | NOT RUN |
| TC-006-02 | UC-006-AC-02 | No opening hours that day | Query date | Empty slots | New test required; not executed | NOT RUN |
| TC-006-03 | UC-006-AC-03 | Active reservation (Sprint 2) | Query overlapping date | Occupied slot is unavailable | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-006-04 | UC-006-AC-04 | Duration below court minimum | Query | 422 | New test required; not executed | NOT RUN |

## UC-007 — Create reservation

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-007-01 | UC-007-AC-01 | Valid free slot | Create booking | 201; PENDING and UNPAID; slot occupied | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-007-02 | UC-007-AC-02 | Same court and occupied interval | Create overlapping booking | 409; original booking intact | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-007-03 | UC-007-AC-03 | Valid free slot | Send 50 concurrent identical requests on PostgreSQL | Exactly one 201 and 49 HTTP 409; one active allocation | scripts/verify_pg_concurrency.py (requires live PostgreSQL; not run) | NOT RUN |
| TC-007-04 | UC-007-AC-04 | Naive/past time, invalid duration or overnight | Create booking | 422; no write | New test required; not executed | NOT RUN |
| TC-007-05 | UC-007-AC-05 | Maintenance or outside hours | Create booking | 409; no write | New test required; not executed | NOT RUN |
| TC-007-06 | UC-007-AC-06 | Price 200000 per hour and 90 minutes | Create booking | Total 300000.00 using decimal arithmetic | New test required; not executed | NOT RUN |

## UC-008 — View and decide bookings

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-008-01 | UC-008-AC-01 | Own PENDING booking | Owning owner approves | 200; CONFIRMED | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-008-02 | UC-008-AC-02 | Player or unrelated owner | Approve | 403 | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts; backend/tests/test_fullstack.py::test_permissions_admin_and_maintenance | NOT RUN |
| TC-008-03 | UC-008-AC-03 | PENDING booking | Owning owner rejects | 200; REJECTED and slot released | New test required; not executed | NOT RUN |
| TC-008-04 | UC-008-AC-04 | Non-PENDING booking | Approve/reject | 409 | New test required; not executed | NOT RUN |
| TC-008-05 | UC-008-AC-05 | Player | List scope=all or scope=owner | 403 | New test required; not executed | NOT RUN |

## UC-009 — Cancel or reschedule reservation

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-009-01 | UC-009-AC-01 | Confirmed unpaid booking | Player reschedules to free slot | 200; PENDING; prior slot reusable | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-009-02 | UC-009-AC-02 | Paid booking before start | Cancel | 200; REFUND_REVIEW and slot released | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts (payment asserted; release needs separate assertion) | NOT RUN |
| TC-009-03 | UC-009-AC-03 | Submitted or paid booking | Reschedule | 409; original reservation unchanged | New test required; not executed | NOT RUN |
| TC-009-04 | UC-009-AC-04 | Booking already started | Cancel | 409 | New test required; not executed | NOT RUN |
| TC-009-05 | UC-009-AC-05 | New slot occupied | Reschedule | 409; original allocation retained | New test required; not executed | NOT RUN |

## UC-010 — Submit and verify demo payment

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-010-01 | UC-010-AC-01 | Confirmed unpaid booking | Submit reference | 200; SUBMITTED | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-010-02 | UC-010-AC-02 | Confirmed submitted reference | Owner confirms | 200; PAID | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts | NOT RUN |
| TC-010-03 | UC-010-AC-03 | Pending booking | Submit reference | 409 | New test required; not executed | NOT RUN |
| TC-010-04 | UC-010-AC-04 | Unsubmitted or non-confirmed booking | Confirm | 409 | New test required; not executed | NOT RUN |

## UC-011 — Read in-app notifications

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-011-01 | UC-011-AC-01 | Booking lifecycle events | Read own notifications | 200; events present | backend/tests/test_fullstack.py::test_book_approve_pay_reschedule_cancel_and_conflicts (existence only) | NOT RUN |
| TC-011-02 | UC-011-AC-02 | Owned unread notification | Mark read | 200; read=true | New test required; not executed | NOT RUN |
| TC-011-03 | UC-011-AC-03 | Another user notification ID | Mark read | 404; no mutation | New test required; not executed | NOT RUN |
| TC-011-04 | UC-011-AC-04 | No token | List | 401 | New test required; not executed | NOT RUN |

## UC-012 — Manage teams and members

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-012-01 | UC-012-AC-01 | Authenticated user | Create team and add member | 201 then 200 | backend/tests/test_fullstack.py::test_tournament_registration_fixture_scores_and_slot_conflict | NOT RUN |
| TC-012-02 | UC-012-AC-02 | Existing member name | Add same name with case change | 409 | New test required; not executed | NOT RUN |
| TC-012-03 | UC-012-AC-03 | Non-captain non-admin | Modify roster | 403 | New test required; not executed | NOT RUN |
| TC-012-04 | UC-012-AC-04 | 40 members | Add one | 409 | New test required; not executed | NOT RUN |

## UC-013 — Create tournament and review registrations

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-013-01 | UC-013-AC-01 | Valid organizer/admin and active sport | Create | 201; OPEN | backend/tests/test_fullstack.py::test_tournament_registration_fixture_scores_and_slot_conflict (admin actor) | NOT RUN |
| TC-013-02 | UC-013-AC-02 | Open tournament and own team | Register then approve | 201 then 200 | backend/tests/test_fullstack.py::test_tournament_registration_fixture_scores_and_slot_conflict | NOT RUN |
| TC-013-03 | UC-013-AC-03 | Already registered team | Register again | 409 | New test required; not executed | NOT RUN |
| TC-013-04 | UC-013-AC-04 | Capacity reached or status not OPEN | Register | 409 | New test required; not executed | NOT RUN |
| TC-013-05 | UC-013-AC-05 | Other organizer | Review registration | 403 | New test required; not executed | NOT RUN |

## UC-014 — Generate fixtures and schedule matches

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-014-01 | UC-014-AC-01 | Four approved round robin teams | Generate fixtures | Six matches | backend/tests/test_fullstack.py::test_tournament_registration_fixture_scores_and_slot_conflict | NOT RUN |
| TC-014-02 | UC-014-AC-02 | Four approved knockout teams | Generate fixtures | Two first-round matches | backend/tests/test_knockout.py::test_knockout_creates_final_and_completes | NOT RUN |
| TC-014-03 | UC-014-AC-03 | Scheduled match occupying a court | Try overlapping booking | 409 | backend/tests/test_fullstack.py::test_tournament_registration_fixture_scores_and_slot_conflict | NOT RUN |
| TC-014-04 | UC-014-AC-04 | Wrong sport / outside tournament dates | Schedule | 422 | New test required; not executed | NOT RUN |
| TC-014-05 | UC-014-AC-05 | Same team scheduled in same tournament at same time on another court | Schedule | 409 | New test required; not executed | NOT RUN |
| TC-014-06 | UC-014-AC-06 | Invalid knockout team count | Generate fixtures | 422 | New test required; not executed | NOT RUN |

## UC-015 — Record results and standings

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-015-01 | UC-015-AC-01 | Four-team knockout | Finish semifinals then final | Final generated; tournament COMPLETED | backend/tests/test_knockout.py::test_knockout_creates_final_and_completes | NOT RUN |
| TC-015-02 | UC-015-AC-02 | Prior round after final created | Edit score | 409 | backend/tests/test_knockout.py::test_knockout_creates_final_and_completes (completed tournament case; earlier-round case still needs test) | NOT RUN |
| TC-015-03 | UC-015-AC-03 | Knockout match | Submit tied score | 422 | New test required; not executed | NOT RUN |
| TC-015-04 | UC-015-AC-04 | Round robin results | Read standings | 3 win / 1 draw / 0 loss; ordered by tie-breaks | backend/tests/test_fullstack.py::test_tournament_registration_fixture_scores_and_slot_conflict (review exact assertions; add tie-break test) | NOT RUN |
| TC-015-05 | UC-015-AC-05 | Open or in-progress tournament | Cancel as organizer | CANCELLED; active match allocations released | New test required; not executed | NOT RUN |

## UC-016 — Maintain sports catalog

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-016-01 | UC-016-AC-01 | Admin | Create sport | 201; available in public list | backend/tests/test_sprint1.py::test_auth_and_admin_sport_access | NOT RUN |
| TC-016-02 | UC-016-AC-02 | Player or unauthenticated user | Create sport | 403 or 401 | backend/tests/test_sprint1.py::test_auth_and_admin_sport_access | NOT RUN |
| TC-016-03 | UC-016-AC-03 | Inactive sport | Public list | Not returned | New test required; not executed | NOT RUN |

## UC-017 — Administer users and overview

| Test ID | AC | Setup / data | Action | Expected | Existing evidence / gap | Actual |
|---|---|---|---|---|---|---|
| TC-017-01 | UC-017-AC-01 | Player | Open admin overview | 403 | backend/tests/test_fullstack.py::test_permissions_admin_and_maintenance | NOT RUN |
| TC-017-02 | UC-017-AC-02 | Admin | Open overview | 200 | backend/tests/test_fullstack.py::test_permissions_admin_and_maintenance | NOT RUN |
| TC-017-03 | UC-017-AC-03 | Current admin | Deactivate self | 409 | backend/tests/test_fullstack.py::test_permissions_admin_and_maintenance | NOT RUN |
| TC-017-04 | UC-017-AC-04 | Other account | Deactivate then attempt login | Login 401 | New test required; not executed | NOT RUN |
