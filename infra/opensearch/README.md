# infra/opensearch

OpenSearch index templates and ILM (Index Lifecycle Management) policy files.

Index plan (see [../../docs/architecture/data-model.md#opensearch-index-plan](../../docs/architecture/data-model.md)):

- `tg365-entra-signins-YYYY.MM` — 13 months
- `tg365-entra-directoryaudits-YYYY.MM` — 24 months
- `tg365-sharepoint-activity-YYYY.MM` — 13 months
- `tg365-exchange-activity-YYYY.MM` — 13 months
- `tg365-teams-activity-YYYY.MM` — 13 months
- `tg365-content-search-results-YYYY.MM` — 6 months
- `tg365-alerts-YYYY.MM` — 24 months

Phase 10+ replaces this README with concrete template JSON the platform
applies at first start.
