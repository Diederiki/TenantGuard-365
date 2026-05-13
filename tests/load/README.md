# tests/load

Load tests for the report engine and audit ingestion path. k6 scripts.

Planned scenarios:
- 50 concurrent technicians running medium-sized reports
- 10k SharePoint sites collected within the throttling budget
- 1M audit events ingested over 1 hour
- Audit viewer paging through deepest cursor at 50/page

Run locally with `k6 run` against a seeded local stack.
