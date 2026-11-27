# ADR-007 — Simulated payment instead of real gateway

Status: Proposed for ratification (existing design reconstructed, not a historical approval). Date recorded: 2026-11-27. Suggested owner: Vũ / Tuấn.

## Context
Course project needs payment workflow demonstration without financial integration.

## Decision
Separate Payment state; user submits reference, owner verifies demo marker, cancellation may flag manual refund review.

## Alternatives considered (proposed review)
Real gateway and webhooks; no payment feature.

## Consequences / trade-offs
Never represent PAID as confirmed bank receipt; no automatic transfer/refund.

## Validation
Review with business/technical representatives. Link relevant UC/AC and test evidence before acceptance.

## Approval
Pending — add real reviewer, date and review reference in ../sdd/REVIEW_LOG.md.
