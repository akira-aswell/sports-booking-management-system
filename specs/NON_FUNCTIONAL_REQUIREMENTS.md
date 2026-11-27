# Quality attributes and nonfunctional requirements

Draft targets; distinguish existing mechanisms from verified results.

| ID | Attribute | Proposed measurable criterion | Verification |
|---|---|---|---|
| NFR-01 | Integrity | One successful creation from 50 valid simultaneous requests for one previously free slot; no overlapping active allocation | PostgreSQL script and SQL checks |
| NFR-02 | Authorization | Unauthenticated protected requests denied; wrong-role and wrong-owner mutation denied; notifications private | Negative API tests |
| NFR-03 | Reproducibility | Fresh clone of submission repo starts using documented Compose procedure and correct migration | Clean-build log and smoke test |
| NFR-04 | Maintainability | Every in-scope AC maps to a test; changes link UC/AC and reviewer | Traceability review |
| NFR-05 | Data security | No real secrets or production/customer data committed; demo credentials local only | Git review; environment check |
| NFR-06 | Usability | Player can find a court and submit booking; owner can review; UI reports conflicts without silent failure | Browser acceptance test |
| NFR-07 | Reliability | Failure to allocate a conflicting slot leaves existing records unchanged | Transaction failure tests |
| NFR-08 | Performance | Record latency and error distribution for 50-request experiment; no fixed latency SLA until measured and agreed | Test log; team-approved target later |

Out of scope: production SLA, payment compliance, multi-tenant hosting, external notification delivery. All verification is pending in this documentation package.
