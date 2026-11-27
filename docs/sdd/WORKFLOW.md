# SDD workflow and human review

The existing prototype predates this baseline. Do not imply otherwise. The specification is a living, versioned engineering artifact; humans own requirements and decisions, AI assists analysis and implementation.

1. Identify BR, UC, relevant AC, business rules and open decisions. Update specification first for new behavior.
2. Business representative reviews intent, edge cases and scope; tech lead reviews design and dependencies. Record actual approvals in REVIEW_LOG.md; no self-approval assumption. Conduct a walkthrough each Sprint.
3. Create a coding plan (affected modules, API/UI/database impacts, risks, tests). Give AI the relevant version-controlled context, not just a prompt.
4. Implement or integrate only agreed changes; review actual diff and security/architecture.
5. Run tests derived from reviewed ACs. Link logs and defect issues; do not replace failed expectations with passing tests just to match code.
6. PR references UC/AC and related decisions, includes reviewer and evidence. Merge after quality gate or explicitly approved risk. Update traceability, docs and test results.

## Definition of ready
Actor, goal, rules, alternatives, testable AC, dependencies and risks agreed; open decisions affecting implementation resolved.

## Definition of done
Actual merged files, reviewed spec, passing required tests or explicitly accepted exception, evidence link, no unresolved critical defects, reproducible integration. File count or commit count is not a quality measure.

## Commit convention
Examples for actual changes only: `docs(UC-007): specify reservation acceptance criteria`; `test(UC-007): verify overlapping slots`; `fix(UC-009): enforce approved reschedule policy`. For existing source imports use `chore(import): ...` and link relevant UC in PR. Never backdate or attribute unperformed work.

## AI handoff
Give AI PROJECT_SCOPE, targeted UC and AC, BUSINESS_RULES, DATABASE_RULES, API_CONTRACTS, relevant ADRs, tests and exact source paths. Ask it to identify conflicts and unclear assumptions, then propose a plan. Human reviewer accepts or rejects. Keep important decisions in Git rather than chat history; don't send credentials or personal data.
