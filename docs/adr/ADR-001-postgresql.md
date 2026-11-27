# ADR-001 — PostgreSQL for relational storage

Status: Proposed for ratification (existing design reconstructed, not a historical approval). Date recorded: 2026-11-27. Suggested owner: Hùng.

## Context
Court/booking/team entities require referential integrity and safe occupancy under concurrent writes.

## Decision
Retain PostgreSQL 16 and Alembic; use SQLite only for lightweight behavior tests.

## Alternatives considered (proposed review)
SQLite for simplicity; MySQL for relational storage but a different overlap strategy; document migration impacts.

## Consequences / trade-offs
PostgreSQL local service and migration privileges are required. SQLite does not supply the same exclusion guarantee.

## Validation
Review with business/technical representatives. Link relevant UC/AC and test evidence before acceptance.

## Approval
Pending — add real reviewer, date and review reference in ../sdd/REVIEW_LOG.md.
