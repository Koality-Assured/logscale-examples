# LogScale Alert & Action Terraform Module

Pairs real-time LogScale filter alerts (`logscale_filter_alert`) with webhook notification actions (`logscale_action`).

## Usage

```hcl
module "root_login_alert" {
  source            = "../modules/alert"
  repository_name   = "aws-cloudtrail-logs"
  alert_name        = "AWS Root Account Console Login"
  alert_description = "Fires immediately when root credentials sign into the AWS console"
  query_string      = "Vendor.eventName = \"ConsoleLogin\" Vendor.userIdentity.type = \"Root\""
  action_name       = "SecurityAlertSlackWebhook"
  webhook_endpoint  = "https://hooks.slack.com/services/EXAMPLE/WEBHOOK/PLACEHOLDER"
}
```
