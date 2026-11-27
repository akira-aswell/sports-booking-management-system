# ADR-002 — FastAPI and SQLAlchemy

Status: Proposed for ratification (existing design reconstructed, not a historical approval). Date recorded: 2026-11-27. Suggested owner: Tuấn.

## Context
Need a validated API between UI and relational database.

## Decision
Retain FastAPI, Pydantic and SQLAlchemy sessions; server checks all authorization.

## Alternatives considered (proposed review)
A monolithic UI/database app or another REST framework.

## Consequences / trade-offs
Team must maintain contracts and transactions, not rely on UI checks.

## Validation
Review with business/technical representatives. Link relevant UC/AC and test evidence before acceptance.

## Approval
Pending — add real reviewer, date and review reference in ../sdd/REVIEW_LOG.md.
