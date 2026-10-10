variable "logscale_api_url" {
  type        = string
  description = "Base API URL for the LogScale cluster (e.g. https://cloud.humio.com)"
  default     = "https://cloud.humio.com"
}

variable "logscale_api_token" {
  type        = string
  description = "Administrative API token with permission to manage repositories, views, parsers, and feeds"
  sensitive   = true
}

variable "environment" {
  type        = string
  description = "Target deployment tier"
  default     = "production"
}

variable "sqs_queue_url" {
  type        = string
  description = "SQS queue URL for the S3-SQS ingest feed"
  default     = "https://sqs.us-east-1.amazonaws.com/123456789012/logscale-ingest-queue-prod"
}

variable "iam_role_arn" {
  type        = string
  description = "Cross-account IAM role ARN assumed by LogScale"
  default     = "arn:aws:iam::123456789012:role/logscale-cross-account-ingest-role-prod"
}

variable "slack_webhook_endpoint" {
  type        = string
  description = "Slack incoming webhook URL for alert notifications"
  default     = "https://hooks.slack.com/services/EXAMPLE/WEBHOOK/PLACEHOLDER"
}
