# S3-to-SQS LogScale Ingest Architecture in Terraform

provider "aws" {
  region = var.aws_region
}

locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "logscale-examples"
    Pipeline    = "s3-sqs-pull-feed"
  }
}

# 1. Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                      = "logscale-ingest-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days
  tags                      = local_common_tags
}

# 2. Main SQS Ingestion Queue
resource "aws_sqs_queue" "ingest" {
  name                      = "logscale-ingest-queue-${var.environment}"
  visibility_timeout_seconds = 300
  message_retention_seconds = 1209600 # 14 days

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })

  tags = local_common_tags
}

# 3. S3 Bucket for Raw Logs
resource "aws_s3_bucket" "logs" {
  bucket = "example-corp-logscale-archive-${var.environment}"
  tags   = local_common_tags
}

resource "aws_s3_bucket_public_access_block" "pab" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sse" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4. SQS Queue Policy granting S3 permission to publish ObjectCreated events
resource "aws_sqs_queue_policy" "s3_notify" {
  queue_url = aws_sqs_queue.ingest.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowS3PublishEvents"
        Effect    = "Allow"
        Principal = { Service = "s3.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.ingest.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.logs.arn
          }
        }
      }
    ]
  })
}

# 5. S3 Bucket Notification
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.logs.id

  queue {
    queue_arn     = aws_sqs_queue.ingest.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "AWSLogs/"
  }

  depends_on = [aws_sqs_queue_policy.s3_notify]
}

# 6. Cross-Account IAM Role assumed by CrowdStrike LogScale
resource "aws_iam_role" "logscale_ingest" {
  name = "logscale-cross-account-ingest-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowLogscaleAssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.logscale_aws_account_id}:role/cs_logscale_granter_role"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.logscale_external_id
          }
        }
      }
    ]
  })

  tags = local_common_tags
}

resource "aws_iam_policy" "logscale_access" {
  name        = "logscale-ingest-access-policy-${var.environment}"
  description = "Allows LogScale to poll SQS notifications and read log archives from S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowSQSPolling"
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = aws_sqs_queue.ingest.arn
      },
      {
        Sid    = "AllowS3Read"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.logs.arn,
          "${aws_s3_bucket.logs.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.logscale_ingest.name
  policy_arn = aws_iam_policy.logscale_access.arn
}

# 7. Declarative LogScale Ingest Feed Resource
resource "logscale_aws_s3_sqs_ingest_feed" "feed" {
  repository_name     = var.logscale_repository_name
  name                = "aws-vpc-flow-ingest-feed-${var.environment}"
  description         = "Automated S3-SQS ingest feed for VPC Flow Logs in ${var.environment}"
  enabled             = true
  parser              = var.logscale_parser_name
  region              = var.aws_region
  sqs_url             = aws_sqs_queue.ingest.id
  compression         = "Auto"
  authentication_kind = "IamRole"
  role_arn            = aws_iam_role.logscale_ingest.arn
  preprocessing_kind  = "SplitNewline"
}
