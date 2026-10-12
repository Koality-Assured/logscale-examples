# LogScale Production Environment Blueprint

End-to-end environment configuration that wires repositories, global views, S3-SQS ingest feeds, and real-time security alerts together using Terraform.

## Execution Runbook

> **Note on Provider Availability**: The `koality-assured/logscale` Terraform provider used in these examples is currently in development and has not yet been published to the public Terraform Registry. To run these examples locally, you will need to build the provider from source and configure a Terraform CLI dev override.

1. Copy the example variable file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
2. Populate `logscale_api_token` with an administrative API token from the LogScale UI (**Account Settings > API Tokens**).
3. Configure a [development override](https://developer.hashicorp.com/terraform/cli/config/config-file#development-overrides) in your `~/.terraformrc` pointing `koality-assured/logscale` to your local provider binary.
4. Plan and apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```
