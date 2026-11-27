# Team handoff and revised milestones (proposed)

Dates are targets from 28 November 2026 onward, not actual commits. Keep existing source history; apply the SDD workflow to future integration and changes.

| Date | Owner | Deliverable / paths | Suggested commit (only after actual review/change) |
|---|---|---|---|
| 28/11 | Khánh + Khoa | specs/README.md, PROJECT_SCOPE.md, business-requirements/, user-stories/ | docs: establish retrospective SDD baseline |
| 29/11 | Hùng | specs/entities/, DATABASE_RULES.md, diagrams/ERD.md, docs/sdd/DATABASE_DESIGN.md, ADR-001/004 | docs(UC-007): document database and allocation rules |
| 29/11 | Vinh | specs/UI_SPECIFICATIONS.md, review UC-003/006/011, integrate notifications UI | docs: review user flows and UI acceptance criteria |
| 30/11 | Vũ | UC-004/005/007/008/009/012/013, BUSINESS_RULES.md | docs(UC-009): review booking lifecycle rules |
| 30/11 | Tuấn | UC-001/002/010/011/014/015, API_CONTRACTS.md, ADR-002/005/006/007 | docs: review API and security contracts |
| 01/12 | Khánh + Khoa | traceability, NFR, diagrams, review log, test plan, open decisions | docs: review specification and traceability baseline |
| 02/12 | Hùng + Tuấn | integrate current runtime dependencies; execute PostgreSQL verification only on running demo | test(UC-007): record verified PostgreSQL concurrency results |
| 03–05/12 | Entire team | Sprint 2 integration, manual QA, actual test logs and fixes | feature-specific PRs linked to UC/AC |
| 06/12 | Khánh + Khoa | Sprint review, gate decision and Sprint 3 priorities | docs: record sprint review and remaining risks |
| 07/12 onward | Entire team | Validate Sprint 3 drafts, plan, implement/import, test, review | UC-specific actual changes |

All documents can be introduced together in one clearly identified SDD baseline PR, then each owner reviews and changes their assigned portion. Do not split identical prewritten docs across members to simulate authorship. If no changes are needed after review, record an actual PR review rather than an empty commit.
