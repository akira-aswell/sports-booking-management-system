# Provenance and references

Prepared 2026-11-27 as a retrospective specification baseline. No source files were changed or executed. The personal prototype is publicly readable; the instructor-facing repository URL was not supplied. The reported imported milestone is the user's screenshot, not a checked git history.

## Course sources
- SDD-Ebook.pdf: chapter 3 (six principles), chapter 5 (Brownfield), section 6.3 (repository structure), appendix (use case template).
- Session 1.pdf: AI-driven lifecycle and shared context.
- Session 2.pdf: requirements, human validation, acceptance criteria, architecture; p.31 AI-Ready Specification summary.
- Session 3.pdf: development context, planning, testing, review and QA quality gates (p.10, p.22).
- Session 4.pdf: p.37–40 iterative, test-protected, stakeholder-centric and traceable principles; p.44 tools are references.

## Prototype inspected
- [README](https://github.com/lehung20306/sports-booking-management-system/blob/main/README.md)
- [API contract reference](https://github.com/lehung20306/sports-booking-management-system/blob/main/docs/API_REFERENCE.md)
- [Booking router](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/api/bookings.py)
- [Scheduling](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/services/scheduling.py)
- [Migration 0002](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/alembic/versions/0002_complete.py)
- [Court router](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/api/courts.py)
- [Auth router](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/api/auth.py)
- [Notifications](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/api/notifications.py)
- [Tournament router](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/api/tournaments.py)
- [Admin router](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/api/admin.py)
- [App entrypoint](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/app/main.py) and [frontend routes](https://github.com/lehung20306/sports-booking-management-system/blob/main/frontend/src/App.tsx)
- [Sprint 1 tests](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/tests/test_sprint1.py), [fullstack tests](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/tests/test_fullstack.py), [fixtures](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/tests/conftest.py), [knockout test](https://github.com/lehung20306/sports-booking-management-system/blob/main/backend/tests/test_knockout.py)
- [Concurrency script](https://github.com/lehung20306/sports-booking-management-system/blob/main/scripts/verify_pg_concurrency.py)

Links point to the source branch, not an immutable SHA. Before review record the actual team commit and verify differences; diagrams and AC targets are reconstructed proposals, not official instructor-imposed filenames. Initial schema/details use the existing project documentation and prior context; verify models and migration 0001 against the checked-out team repo. No live deployment or test execution was verified.
