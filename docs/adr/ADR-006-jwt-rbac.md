# ADR-006 — JWT and role/ownership authorization

Status: Proposed for ratification (existing design reconstructed, not a historical approval). Date recorded: 2026-11-27. Suggested owner: Tuấn.

## Context
Different users access different operations; identity must be verified on server.

## Decision
Use bearer JWT and server-side role plus resource ownership checks; restrict public registration.

## Alternatives considered (proposed review)
Server-side sessions or external identity provider.

## Consequences / trade-offs
Token management and security hardening needed before production; no claim of full security coverage.

## Validation
Review with business/technical representatives. Link relevant UC/AC and test evidence before acceptance.

## Approval
Pending — add real reviewer, date and review reference in ../sdd/REVIEW_LOG.md.
