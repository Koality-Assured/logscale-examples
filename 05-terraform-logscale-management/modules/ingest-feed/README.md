# LogScale S3-SQS Ingest Feed Terraform Module

Declaratively connects an AWS S3 bucket and SQS notification queue to a LogScale repository via the `logscale_aws_s3_sqs_ingest_feed` resource.

## Usage

```hcl
module "vpc_flow_feed" {
  source          = "../modules/ingest-feed"
  repository_name = "aws-vpc-flow-logs"
  feed_name       = "prod-vpc-flow-feed"
  parser_name     = "aws-vpc-flow"
  aws_region      = "us-east-1"
  sqs_queue_url   = "https://sqs.us-east-1.amazonaws.com/123456789012/logscale-ingest-queue-prod"
  iam_role_arn    = "arn:aws:iam::123456789012:role/logscale-cross-account-ingest-role-prod"
}
```
