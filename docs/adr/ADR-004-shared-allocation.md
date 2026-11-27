# ADR-004 — Shared court allocation and overlap protection

Status: Proposed for ratification (existing design reconstructed, not a historical approval). Date recorded: 2026-11-27. Suggested owner: Hùng.

## Context
Reservations and tournament matches compete for the same court; check-then-insert alone can race.

## Decision
Use one allocation row per booking or match, half-open time range, active flag, per-court row lock and PostgreSQL GiST exclusion.

## Alternatives considered (proposed review)
Separate booking/match exclusion constraints (miss cross-context overlap); application-only precheck (race); time-slot buckets (less flexible).

## Consequences / trade-offs
Requires btree_gist; conflicts mapped to 409; buffer policy and cross-module tests essential.

## Validation
Review with business/technical representatives. Link relevant UC/AC and test evidence before acceptance.

## Approval
Pending — add real reviewer, date and review reference in ../sdd/REVIEW_LOG.md.
