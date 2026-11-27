# Sprint 2 integration — corrective plan

The team reports the milestone through 28 November imported: 0002_complete.py, services/__init__.py, scheduling.py, bookings.py, BookingsPage.tsx, notifications.py. These files alone cannot demonstrate a working release. The personal prototype has full entrypoints referencing future modules. The actual submission repository was not accessible, so inspect its files first.

| Task | Suggested owner | Required action / dependency | Completion evidence |
|---|---|---|---|
| INT-01 | Khánh | Review current main and exact imports, open integration PR with honest source origin | Git SHA, file list, agreed scope |
| INT-02 | Tuấn | Ensure backend app/main.py registers Sprint 1/2 routers; review models/schemas, services, requirements, security and Docker entrypoint dependencies | /api/health and /docs from team branch |
| INT-03 | Hùng | Verify 0001 → 0002 on new DB and seed dependencies; if seed imports future models, use a compatible Sprint 2 seed or clearly label full seed data | actual revision and SQL log |
| INT-04 | Vinh | Integrate NotificationsPage.tsx and App.tsx/route imports, Layout.tsx navigation and api/types; no unresolved imports | frontend build and browser navigation |
| INT-05 | Vũ | Verify CourtPage booking submission, BookingsPage mine and owner mode, OwnerPage navigation; payment and cancel/reschedule | recorded walkthrough |
| INT-06 | Khoa | Import relevant Postman/test files, scope suite to implemented routes and review AC gaps | test output and issues |
| INT-07 | Hùng | Run PostgreSQL concurrency script on free interval | actual counts and SQL evidence |
| INT-08 | Khánh | Review integration gate; merge after review; update README scope and link specs | reviewer and release/PR reference |

## Choose one integration strategy
A: Sprint 2-only runnable branch (recommended for Sprint Review). Explicitly adapt main.py, App.tsx, Layout.tsx and seed where necessary; keep existing combined migration because already applied. Do not simply copy full entrypoints while omitting referenced future pages/routers. Review actual files, build and test. B: import every required module from the full prototype, identify it as full prototype; limit the presentation to reviewed Sprint 2 flows. Neither option requires falsifying prior commits. This package does not contain replacement entrypoints because the actual team repository is not available.

## Suggested order
Scope/review specs → integration PR → Docker smoke → targeted tests → concurrency → QA gate → Sprint Review. Do not delay entrypoints until the final sprint. Stop and fix import/migration/build errors before declaring a feature integrated.
