output "s3_bucket_name" {
  description = "Name of the S3 bucket receiving raw log files"
  value       = aws_s3_bucket.logs.id
}

output "sqs_queue_url" {
  description = "URL of the SQS queue delivering notifications to LogScale"
  value       = aws_sqs_queue.ingest.id
}

output "sqs_queue_arn" {
  description = "ARN of the SQS queue"
  value       = aws_sqs_queue.ingest.arn
}

output "logscale_role_arn" {
  description = "ARN of the cross-account role assumed by CrowdStrike LogScale"
  value       = aws_iam_role.logscale_ingest.arn
}
