# AI-ready project context

Use this as a shared context index rather than a new tool framework. The canonical requirements are in ../../specs. The project already has a prototype; treat reconstructed specs as draft until reviewed. The submission repo status is separate from the personal prototype.

## Constraints
Retain React/TypeScript, FastAPI, SQLAlchemy, PostgreSQL/Alembic and Docker Compose unless a reviewed ADR changes them. Payments are simulation only. Preserve existing applied migrations; do not hardcode secrets. Validate role and ownership in backend. Shared court allocation must protect booking and match intervals. Vietnam local time for schedules; UTC storage/comparison. Never invent successful tests or approvals.

## Example task prompt
Read specs/use-cases/UC-007.md, specs/DATABASE_RULES.md, docs/adr/ADR-004-shared-allocation.md and the current implementation/tests. Identify missing context and discrepancies. Propose a plan with exact files, AC/TC IDs, impact and test strategy. Do not change behavior until reviewer confirms the relevant policy. After implementing, show actual diff, test output and remaining risks. Never overwrite unrelated code.

## Repository references
Backend logic: backend/app/api, core, services, models.py, schemas.py. UI: frontend/src/pages, App.tsx, auth.tsx, api.ts. Migrations: backend/alembic/versions. Tests: backend/tests, scripts. Start with actual Git commit and existing source; the source prototype references are documented in SOURCE_REFERENCES.md.
