"""Pulumi Python script for managing serverless API ingestion Lambdas and EventBridge schedules.

Declaratively provisions:
- Lambda functions for each third-party SaaS log product (Okta, GitHub, Snyk, GCP Audit).
- IAM execution roles with least-privilege Secrets Manager and CloudWatch Logs access.
- EventBridge Scheduler ScheduleGroup and cron schedules for each poller.
- Dedicated SQS Dead-Letter Queues (DLQs) to capture failed executions.
"""

import json
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
environment = config.get("environment") or "production"

common_tags = {
    "Environment": environment,
    "ManagedBy": "Pulumi",
    "Project": "logscale-examples",
    "Component": "serverless-api-pollers",
}

# Declarative matrix of SaaS poller products
api_ingest_products = {
    "okta": {
        "schedule_interval_minutes": 2,
        "timeout_seconds": 300,
        "memory_size": 256,
        "handler_path": "../lambdas/okta",
        "state": "ENABLED",
    },
    "github": {
        "schedule_interval_minutes": 5,
        "timeout_seconds": 300,
        "memory_size": 256,
        "handler_path": "../lambdas/github",
        "state": "ENABLED",
    },
    "snyk": {
        "schedule_interval_minutes": 15,
        "timeout_seconds": 300,
        "memory_size": 256,
        "handler_path": "../lambdas/snyk",
        "state": "ENABLED",
    },
    "gcp-audit": {
        "schedule_interval_minutes": 5,
        "timeout_seconds": 300,
        "memory_size": 256,
        "handler_path": "../lambdas/gcp-audit",
        "state": "ENABLED",
    },
}

# EventBridge Scheduler Schedule Group
schedule_group = aws.scheduler.ScheduleGroup(
    "logscale-ingest-schedule-group",
    name=f"logscale-api-ingest-{environment}",
    tags=common_tags,
)

# Shared IAM Assume Role policy for Lambda
lambda_assume_role = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    type="Service",
                    identifiers=["lambda.amazonaws.com"],
                )
            ],
        )
    ]
)

# IAM Assume Role policy for EventBridge Scheduler
scheduler_assume_role = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    type="Service",
                    identifiers=["scheduler.amazonaws.com"],
                )
            ],
        )
    ]
)

scheduler_role = aws.iam.Role(
    "scheduler-execution-role",
    name=f"logscale-scheduler-execution-role-{environment}",
    assume_role_policy=scheduler_assume_role.json,
    tags=common_tags,
)

# Provision resources per product
for product_name, spec in api_ingest_products.items():
    # 1. Dead-letter queue
    dlq = aws.sqs.Queue(
        f"dlq-{product_name}",
        name=f"dlq-logscale-ingest-{product_name}-{environment}",
        message_retention_seconds=1209600,
        tags=common_tags,
    )

    # 2. IAM Role for Lambda
    role = aws.iam.Role(
        f"role-{product_name}",
        name=f"role-logscale-ingest-{product_name}-{environment}",
        assume_role_policy=lambda_assume_role.json,
        tags=common_tags,
    )

    # Attach basic execution policy
    aws.iam.RolePolicyAttachment(
        f"basic-exec-{product_name}",
        role=role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )

    # Custom inline policy for Secrets Manager
    secrets_policy = aws.iam.RolePolicy(
        f"secrets-access-{product_name}",
        role=role.name,
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["secretsmanager:GetSecretValue"],
                    "Resource": f"arn:aws:secretsmanager:*:*:secret:logscale/{product_name}-*",
                }
            ],
        }),
    )

    # 3. Lambda Function
    fn = aws.lambda_.Function(
        f"lambda-{product_name}",
        name=f"logscale-ingest-{product_name}-{environment}",
        role=role.arn,
        runtime="python3.12",
        handler="lambda_function.lambda_handler",
        timeout=spec["timeout_seconds"],
        memory_size=spec["memory_size"],
        code=pulumi.AssetArchive({
            ".": pulumi.FileArchive(spec["handler_path"])
        }),
        dead_letter_config=aws.lambda_.FunctionDeadLetterConfigArgs(
            target_arn=dlq.arn,
        ),
        environment=aws.lambda_.FunctionEnvironmentArgs(
            variables={
                "ENVIRONMENT": environment,
                f"{product_name.upper().replace('-', '_')}_SECRET_NAME": f"logscale/{product_name}-credentials",
            }
        ),
        tags=common_tags,
    )

    # 4. EventBridge Schedule
    interval = spec["schedule_interval_minutes"]
    schedule_expression = f"rate({interval} minutes)"

    # Grant Scheduler permission to invoke this Lambda
    invoke_policy = aws.iam.RolePolicy(
        f"scheduler-invoke-{product_name}",
        role=scheduler_role.name,
        policy=fn.arn.apply(
            lambda fn_arn: json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["lambda:InvokeFunction"],
                        "Resource": fn_arn,
                    }
                ],
            })
        ),
    )

    schedule = aws.scheduler.Schedule(
        f"schedule-{product_name}",
        name=f"schedule-logscale-ingest-{product_name}-{environment}",
        group_name=schedule_group.name,
        schedule_expression=schedule_expression,
        state=spec["state"],
        flexible_time_window=aws.scheduler.ScheduleFlexibleTimeWindowArgs(
            mode="OFF",
        ),
        target=aws.scheduler.ScheduleTargetArgs(
            arn=fn.arn,
            role_arn=scheduler_role.arn,
            retry_policy=aws.scheduler.ScheduleTargetRetryPolicyArgs(
                maximum_retry_attempts=2,
                maximum_event_age_in_seconds=300,
            ),
            dead_letter_config=aws.scheduler.ScheduleTargetDeadLetterConfigArgs(
                arn=dlq.arn,
            ),
        ),
        opts=pulumi.ResourceOptions(depends_on=[invoke_policy]),
    )
