variable "environment" {
  type        = string
  description = "Target deployment environment (e.g., prod, staging, dev)"
  default     = "prod"
}

variable "aws_region" {
  type        = string
  description = "AWS region for the S3 bucket and SQS queue"
  default     = "us-east-1"
}

variable "logscale_aws_account_id" {
  type        = string
  description = "CrowdStrike LogScale AWS account ID authorized to assume the ingest role"
  default     = "426876924399"
}

variable "logscale_external_id" {
  type        = string
  description = "Unique ExternalId generated in LogScale to prevent confused-deputy attacks"
  sensitive   = true
}

variable "logscale_repository_name" {
  type        = string
  description = "Target LogScale repository name to ingest logs into"
  default     = "aws-vpc-flow-logs"
}

variable "logscale_parser_name" {
  type        = string
  description = "Parser to apply upon ingestion"
  default     = "aws-vpc-flow"
}
