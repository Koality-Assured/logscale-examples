# Okta System Log Poller Lambda

Serverless function that queries Okta's System Log API (`/api/v1/logs`) on a scheduled cadence and forwards identity and audit events to LogScale.

## Key Features

1. **RFC 5988 Cursor Pagination**: Okta returns pagination links in the HTTP `Link` header (`rel="next"`). The poller iterates across all subsequent pages until the latest events are caught up.
2. **HTTP 429 Rate-Limit Handling**: Automatically inspects `X-Rate-Limit-Reset` and backs off dynamically when rate limits are approached.
3. **LogScale Structured Ingest API**: Formats events into LogScale's `/api/v1/ingest/humio-structured` JSON schema with tags for indexed routing.

## Secrets Manager Schema

Stored under AWS Secrets Manager secret `logscale/okta-credentials`:

```json
{
  "okta_domain": "example.okta.com",
  "okta_api_token": "00xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "logscale_url": "https://cloud.humio.com",
  "logscale_ingest_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```
