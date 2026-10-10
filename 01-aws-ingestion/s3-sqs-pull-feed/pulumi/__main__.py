"""Pulumi Python program for AWS S3 to SQS LogScale ingest pipeline.

Provisions:
1. S3 bucket for raw logs (VPC Flow Logs, ALB Access Logs, CloudTrail) with SSE-S3 encryption and public access blocks.
2. SQS queue with Dead Letter Queue (DLQ) for ingestion notifications.
3. SQS queue policy granting s3.amazonaws.com permission to publish ObjectCreated events.
4. S3 BucketNotification connecting object creation to the SQS queue.
5. Cross-account IAM role trusted by CrowdStrike LogScale with an ExternalId condition.
"""

import json
import pulumi
import pulumi_aws as aws

# Configuration parameters
config = pulumi.Config()
environment = config.get("environment") or "production"
logscale_aws_account = config.get("logscale_aws_account") or "426876924399"  # Standard CrowdStrike LogScale ingest account
external_id = config.require_secret("logscale_external_id")

common_tags = {
    "Environment": environment,
    "ManagedBy": "Pulumi",
    "Project": "logscale-examples",
    "Component": "s3-sqs-ingest-pipeline",
}

# 1. Dead Letter Queue for failed notification processing
dlq = aws.sqs.Queue(
    "logscale-ingest-dlq",
    name=f"logscale-ingest-dlq-{environment}",
    message_retention_seconds=1209600,  # 14 days
    tags=common_tags,
)

# 2. Main SQS Ingestion Queue
redrive_policy = dlq.arn.apply(
    lambda arn: json.dumps({
        "deadLetterTargetArn": arn,
        "maxReceiveCount": 5,
    })
)

ingest_queue = aws.sqs.Queue(
    "logscale-ingest-queue",
    name=f"logscale-ingest-queue-{environment}",
    visibility_timeout_seconds=300,
    message_retention_seconds=1209600,  # 14 days
    redrive_policy=redrive_policy,
    tags=common_tags,
)

# 3. Log Archive S3 Bucket
log_bucket = aws.s3.Bucket(
    "logscale-archive-bucket",
    bucket=f"example-corp-logscale-archive-{environment}",
    tags=common_tags,
)

# Enforce S3 best practices: Public Access Block, Versioning, and SSE Encryption
aws.s3.BucketPublicAccessBlock(
    "logscale-archive-bucket-pab",
    bucket=log_bucket.id,
    block_public_acls=True,
    block_public_policy=True,
    ignore_public_acls=True,
    restrict_public_buckets=True,
)

aws.s3.BucketServerSideEncryptionConfigurationV2(
    "logscale-archive-bucket-encryption",
    bucket=log_bucket.id,
    rules=[
        aws.s3.BucketServerSideEncryptionConfigurationV2RuleArgs(
            apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationV2RuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm="AES256",
            ),
        ),
    ],
)

# 4. SQS Queue Policy granting S3 permission to publish events
queue_policy_doc = pulumi.Output.all(ingest_queue.arn, log_bucket.arn).apply(
    lambda args: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowS3PublishEvents",
                "Effect": "Allow",
                "Principal": {"Service": "s3.amazonaws.com"},
                "Action": "sqs:SendMessage",
                "Resource": args[0],
                "Condition": {
                    "ArnEquals": {
                        "aws:SourceArn": args[1],
                    },
                },
            }
        ],
    })
)

queue_policy = aws.sqs.QueuePolicy(
    "logscale-ingest-queue-policy",
    queue_url=ingest_queue.url,
    policy=queue_policy_doc,
)

# 5. S3 Bucket Notification wiring S3 object creation to SQS
aws.s3.BucketNotification(
    "logscale-archive-bucket-notification",
    bucket=log_bucket.id,
    queues=[
        aws.s3.BucketNotificationQueueArgs(
            queue_arn=ingest_queue.arn,
            events=["s3:ObjectCreated:*"],
        ),
    ],
    opts=pulumi.ResourceOptions(depends_on=[queue_policy]),
)

# 6. Cross-Account IAM Role for CrowdStrike LogScale
assume_role_policy = external_id.apply(
    lambda ext_id: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowLogscaleAssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{logscale_aws_account}:role/cs_logscale_granter_role",
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": ext_id,
                    },
                },
            }
        ],
    })
)

logscale_role = aws.iam.Role(
    "logscale-ingest-role",
    name=f"logscale-cross-account-ingest-role-{environment}",
    assume_role_policy=assume_role_policy,
    tags=common_tags,
)

# Grant LogScale permissions to poll SQS and read S3 objects
access_policy_doc = pulumi.Output.all(ingest_queue.arn, log_bucket.arn).apply(
    lambda args: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSQSPolling",
                "Effect": "Allow",
                "Action": [
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                    "sqs:GetQueueUrl",
                    "sqs:ChangeMessageVisibility",
                ],
                "Resource": args[0],
            },
            {
                "Sid": "AllowS3ReadObjects",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket",
                ],
                "Resource": [
                    args[1],
                    f"{args[1]}/*",
                ],
            },
        ],
    })
)

logscale_policy = aws.iam.Policy(
    "logscale-ingest-policy",
    name=f"logscale-ingest-policy-{environment}",
    description="Permits CrowdStrike LogScale to poll SQS and read log archives from S3",
    policy=access_policy_doc,
)

aws.iam.RolePolicyAttachment(
    "logscale-ingest-role-attachment",
    role=logscale_role.name,
    policy_arn=logscale_policy.arn,
)

# Outputs
pulumi.export("bucket_name", log_bucket.bucket)
pulumi.export("queue_url", ingest_queue.url)
pulumi.export("queue_arn", ingest_queue.arn)
pulumi.export("role_arn", logscale_role.arn)
