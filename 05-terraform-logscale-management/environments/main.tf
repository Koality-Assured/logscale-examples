# Complete LogScale Production Deployment Blueprint

# 1. Target Repositories
module "repo_vpc_flow" {
  source                = "../modules/repository"
  repository_name       = "aws-vpc-flow-logs"
  description           = "AWS VPC Flow logs across production accounts"
  retention_days        = 90
  storage_size_limit_gb = 2000
  create_federated_view = false
}

module "repo_cloudtrail" {
  source                = "../modules/repository"
  repository_name       = "aws-cloudtrail-logs"
  description           = "AWS CloudTrail management and data events"
  retention_days        = 365
  storage_size_limit_gb = 5000
  create_federated_view = false
}

module "repo_okta" {
  source                = "../modules/repository"
  repository_name       = "okta-audit-logs"
  description           = "Okta enterprise authentication and system logs"
  retention_days        = 180
  storage_size_limit_gb = 1000
  create_federated_view = false
}

# 2. Central Federated View spanning all repositories
resource "logscale_view" "unified_view" {
  name        = "enterprise-unified-logs-view"
  description = "Central cross-repository query view for SOC and compliance"
  repository_names = [
    module.repo_vpc_flow.repository_name,
    module.repo_cloudtrail.repository_name,
    module.repo_okta.repository_name
  ]
}

# 3. S3-SQS Ingest Feed for VPC Flow Logs
module "feed_vpc_flow" {
  source          = "../modules/ingest-feed"
  repository_name = module.repo_vpc_flow.repository_name
  feed_name       = "central-vpc-flow-feed-${var.environment}"
  description     = "Automated S3-SQS feed for VPC Flow logs in ${var.environment}"
  parser_name     = "aws-vpc-flow"
  aws_region      = "us-east-1"
  sqs_queue_url   = var.sqs_queue_url
  iam_role_arn    = var.iam_role_arn
}

# 4. Critical Security Alert (Root Account Login)
module "alert_root_login" {
  source            = "../modules/alert"
  repository_name   = module.repo_cloudtrail.repository_name
  alert_name        = "AWS Root Account Console Login"
  alert_description = "Critical alert fired when interactive AWS root credentials sign in"
  query_string      = "Vendor.eventName = \"ConsoleLogin\" Vendor.userIdentity.type = \"Root\" #event.outcome = \"success\""
  action_name       = "SecurityAlertSlackWebhook"
  webhook_endpoint  = var.slack_webhook_endpoint
  body_template     = "{\"text\":\"*CRITICAL ALERT*: AWS Root Account Login detected in {repo_name} at {triggered_timestamp}\"}"
}
