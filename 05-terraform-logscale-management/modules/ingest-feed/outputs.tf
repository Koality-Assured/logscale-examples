output "feed_id" {
  description = "Identifier of the created S3-SQS ingest feed"
  value       = logscale_aws_s3_sqs_ingest_feed.feed.id
}
