# LogScale Production Environment Blueprint

End-to-end environment configuration that wires repositories, global views, S3-SQS ingest feeds, and real-time security alerts together using Terraform.

## Execution Runbook

1. Copy the example variable file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
2. Populate `logscale_api_token` with an administrative API token from the LogScale UI (**Account Settings > API Tokens**).
3. Plan and apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```
