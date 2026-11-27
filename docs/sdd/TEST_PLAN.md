# Quality engineering and acceptance plan

Owner: Khoa, with feature owners. Source tests are mapped in TEST_CASES.md and ../../specs/TRACEABILITY_MATRIX.md. All test executions are pending for this package.

## Environments and tests
- Unit/API behavior: pytest with existing SQLite fixtures from backend/tests/conftest.py. Verify exact test file exists and app imports before running.
- Integration: real PostgreSQL + backend + frontend; test migrations, data seed, API, UI and authorization.
- Concurrency: 50 concurrent identical valid booking requests on a previously free slot. PostgreSQL only; see POSTGRES_VERIFICATION.md. Expected one 201, 49 409; any other distribution requires investigation, not a pass.
- Browser: public search, owner update, player booking, owner approval, payment simulation, notifications, cancellation and conflicting request. Sprint 3 tests only after corresponding modules integrated.

## Commands (PowerShell, project root)
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose config --services
docker compose up --build -d
docker compose ps
docker compose logs --tail 80 backend
```
API / UI endpoints depend on actual compose.yaml; confirm published ports with `docker compose ps`. Fullstack source defaults are 8000 and 5173. Do not run these commands in a non-runnable partial repo before resolving integration dependencies.

For Python tests on a local Python environment (backend folder):
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q tests/test_sprint1.py
```
After importing the full suite and its dependencies, run `python -m pytest -q` with the same environment. Existing test_fullstack.py contains both Sprint 2 and Sprint 3 tests, so select relevant nodes for a Sprint 2-only app. `test_permissions_admin_and_maintenance` also imports/uses admin/team functionality; split or select after review. Do not treat suite failures due to missing routes as accepted.

## Quality gates
Development: reviewed spec, completed plan, code review, unit test evidence, no critical unresolved defects. QA: mapped ACs, actual pass/fail, defect triage, regression and explicit release decision. Record evidence in TEST_EXECUTION_LOG.md and issues. No fabricated pass counts or coverage.
