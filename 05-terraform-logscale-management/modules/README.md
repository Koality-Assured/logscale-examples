# Reusable Terraform Modules for LogScale

Production Terraform modules for managing CrowdStrike Falcon LogScale resources declaratively using `terraform-provider-logscale`.

## Module Directory

- **[`repository/`](./repository/)**: Manages `logscale_repository` (retention days, storage size limit) and companion `logscale_view` federated views.
- **[`parser/`](./parser/)**: Manages `logscale_parser` with external script file references and tag field assignments.
- **[`ingest-feed/`](./ingest-feed/)**: Manages `logscale_aws_s3_sqs_ingest_feed` to pull logs from S3 buckets via SQS notifications.
- **[`alert/`](./alert/)**: Manages `logscale_filter_alert` paired with `logscale_action` (webhooks).
