# S3-SQS Ingest Pipeline (Pulumi Python)

Pulumi program that provisions the complete AWS-side infrastructure for LogScale S3-SQS pull feeds:

- Hardened S3 bucket with default SSE encryption and public access blocks.
- Ingestion SQS queue with 14-day retention and a connected Dead Letter Queue (DLQ).
- SQS QueuePolicy allowing `s3.amazonaws.com` to deliver `s3:ObjectCreated:*` notifications.
- S3 BucketNotification connecting the bucket to the queue.
- Cross-account IAM role with LogScale trust policy and ExternalId verification.

## Deployment

```bash
pulumi stack init prod
pulumi config set aws:region us-east-1
pulumi config set --secret logscale_external_id "your-logscale-external-id"
pulumi preview
```
