# GitHub Enterprise Audit Log Poller Lambda

Serverless log ingestion function designed to poll the GitHub REST API (`/orgs/{org}/audit-log`) on an EventBridge schedule and push audit events into CrowdStrike Falcon LogScale.

## Key Features

1. **ETag Conditional Requests**: Saves HTTP `ETag` headers to `/tmp/github-etag-cache.json`. When polled during low-activity windows, GitHub responds with `304 Not Modified`, saving precious API rate limit quota (5,000 req/hr limit).
2. **Overlapping Lookback Window**: For a 5-minute execution interval, the poller uses a 7-minute lookback filter (`phrase=created:>=...`). This 2-minute safety overlap prevents log loss from clock skew or delayed GitHub internal indexing.
3. **HTTP Event Collector (HEC) Ingestion**: Submits events formatted as newline-delimited JSON (NDJSON) to LogScale's `/api/v1/ingest/hec/raw` endpoint.

## Secrets Manager Schema

Stored under AWS Secrets Manager secret `logscale/github-credentials`:

```json
{
  "github_org": "example-corp",
  "github_pat": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "logscale_url": "https://cloud.humio.com",
  "logscale_ingest_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```
