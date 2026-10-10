# IAM Policies for LogScale Cross-Account Ingestion

Contains standalone JSON policy documents used to configure cross-account access between your AWS account and CrowdStrike Falcon LogScale.

## Files

- [`trust_policy.json`](./trust_policy.json): STS AssumeRole policy with `sts:ExternalId` condition allowing LogScale's official ingest role (`arn:aws:iam::426876924399:role/cs_logscale_granter_role`) to assume the role.
- [`permissions_policy.json`](./permissions_policy.json): IAM permissions policy granting `s3:GetObject` on the log archive bucket and SQS polling actions (`sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:ChangeMessageVisibility`).
