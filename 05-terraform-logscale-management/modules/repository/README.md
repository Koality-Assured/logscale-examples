# LogScale Repository Terraform Module

Provisions a target repository and an optional companion federated view in CrowdStrike Falcon LogScale.

## Usage

```hcl
module "aws_cloudtrail_repo" {
  source                = "../modules/repository"
  repository_name       = "aws-cloudtrail-logs"
  description           = "Production AWS CloudTrail audit logs"
  retention_days        = 365
  storage_size_limit_gb = 5000
  create_federated_view = true
}
```
