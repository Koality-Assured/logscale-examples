# Sigma-to-LogScale Compiler

Python utility that parses Sigma detection YAML files, compiles selection criteria into native CrowdStrike Falcon LogScale CQL query strings, and generates declarative Terraform alert resources (`logscale_filter_alert` or `logscale_aggregate_alert`).

## Usage

```bash
python sigma_to_logscale.py ../rules/aws-cloudtrail-root-login.yaml
```

Output:
```text
============================================================
 TITLE: AWS Root Account Console Login
 TARGET REPO: aws-cloudtrail-logs
 ALERT TYPE:  logscale_filter_alert
------------------------------------------------------------
 GENERATED CQL:
 #repo = "aws-cloudtrail-logs" Vendor.eventName = "ConsoleLogin" Vendor.userIdentity.type = "Root" #event.outcome = "success"
------------------------------------------------------------
 TERRAFORM RESOURCE:
resource "logscale_filter_alert" "aws_cloudtrail_root_login" {
  repository_name = "aws-cloudtrail-logs"
  name            = "AWS Root Account Console Login"
  description     = "Detects interactive console sign-ins using AWS Root account credentials."
  query_string    = "#repo = \"aws-cloudtrail-logs\" Vendor.eventName = \"ConsoleLogin\" Vendor.userIdentity.type = \"Root\" #event.outcome = \"success\""
  enabled         = true
}
============================================================
```
