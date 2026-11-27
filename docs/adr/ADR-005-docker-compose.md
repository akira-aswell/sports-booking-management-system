# ADR-005 — Docker Compose local development

Status: Proposed for ratification (existing design reconstructed, not a historical approval). Date recorded: 2026-11-27. Suggested owner: Tuấn.

## Context
Members need repeatable environment without configuring each dependency manually.

## Decision
Keep database/backend/frontend in one local Compose stack; local volumes independent by default.

## Alternatives considered (proposed review)
Native install of Python, Node and PostgreSQL; hosted shared stack.

## Consequences / trade-offs
Docker Desktop/Engine required; local DB is not shared; clean clone must be checked.

## Validation
Review with business/technical representatives. Link relevant UC/AC and test evidence before acceptance.

## Approval
Pending — add real reviewer, date and review reference in ../sdd/REVIEW_LOG.md.
