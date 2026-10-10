terraform {
  required_version = ">= 1.5.0"
  required_providers {
    logscale = {
      source  = "koality-assured/logscale"
      version = "~> 0.1.0"
    }
  }
}

resource "logscale_aws_s3_sqs_ingest_feed" "feed" {
  repository_name     = var.repository_name
  name                = var.feed_name
  description         = var.description
  enabled             = var.enabled
  parser              = var.parser_name
  region              = var.aws_region
  sqs_url             = var.sqs_queue_url
  compression         = "Auto"
  authentication_kind = "IamRole"
  role_arn            = var.iam_role_arn
  preprocessing_kind  = "SplitNewline"
}
