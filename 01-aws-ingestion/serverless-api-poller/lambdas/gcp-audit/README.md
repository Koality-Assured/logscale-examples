# GCP Cloud Audit Poller Lambda

Serverless function forwarding Google Cloud Platform (GCP) audit logs, GKE administrative events, and IAM changes to CrowdStrike LogScale.

## Secrets Manager Schema

Stored under AWS Secrets Manager secret `logscale/gcp-credentials`:

```json
{
  "gcp_project_id": "example-prod-project",
  "gcp_service_account_key": "{\"type\": \"service_account\", ...}",
  "logscale_url": "https://cloud.humio.com",
  "logscale_ingest_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```
