# Snyk Security & Audit Poller Lambda

Serverless poller collecting vulnerability scan results, dependency posture, and administrative audit logs from Snyk into LogScale.

## Secrets Manager Schema

Stored under AWS Secrets Manager secret `logscale/snyk-credentials`:

```json
{
  "snyk_org_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "snyk_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "logscale_url": "https://cloud.humio.com",
  "logscale_ingest_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```
