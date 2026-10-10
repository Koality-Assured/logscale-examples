variable "repository_name" {
  type        = string
  description = "Target repository receiving log streams"
}

variable "feed_name" {
  type        = string
  description = "Descriptive name for the S3-SQS ingest feed"
}

variable "description" {
  type        = string
  description = "Human-readable description"
  default     = "Managed S3-SQS ingest feed"
}

variable "enabled" {
  type        = bool
  description = "Whether the ingest feed is actively processing messages"
  default     = true
}

variable "parser_name" {
  type        = string
  description = "Name of the parser assigned to this feed"
}

variable "aws_region" {
  type        = string
  description = "AWS Region where the SQS queue resides"
}

variable "sqs_queue_url" {
  type        = string
  description = "Full URL of the SQS queue receiving S3 object creation notifications"
}

variable "iam_role_arn" {
  type        = string
  description = "ARN of the cross-account IAM role assumed by LogScale"
}
