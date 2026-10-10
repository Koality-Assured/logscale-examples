# S3-SQS Ingest Pipeline (Terraform)

Terraform module that provisions AWS log archiving infrastructure and wires it directly to CrowdStrike Falcon LogScale via the `logscale_aws_s3_sqs_ingest_feed` resource.

## Resource Graph

1. `aws_s3_bucket.logs`: Target bucket storing raw compressed logs (VPC flow logs, ALB logs).
2. `aws_sqs_queue.ingest`: SQS queue receiving S3 object creation notifications.
3. `aws_sqs_queue.dlq`: Dead-letter queue capturing failed messages after 5 retries.
4. `aws_iam_role.logscale_ingest`: Cross-account role assumed by LogScale.
5. `logscale_aws_s3_sqs_ingest_feed.feed`: Declarative LogScale ingest feed definition.

## Quickstart

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
```
