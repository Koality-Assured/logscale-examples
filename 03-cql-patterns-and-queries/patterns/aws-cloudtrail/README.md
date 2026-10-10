# AWS CloudTrail Query Patterns

Validated CrowdStrike Falcon LogScale query patterns for threat detection, IAM auditing, and administrative governance in AWS CloudTrail.

## Target Repository
- Repository: `aws-cloudtrail-logs`

## Key Patterns Overview

1. **Root Account Console Login**: Identifies sensitive logins using the root user credentials.
2. **AccessDenied Bursts**: Highlights privilege enumeration or misconfigured IAM roles encountering permission failures.
3. **Security Group 0.0.0.0/0 Exposure**: Alerts when public ingress rules are attached to EC2 security groups.
4. **S3 Public Bucket Policy Modifications**: Tracks deletions or updates to S3 bucket security policies.
5. **Human Write Activity Discovery**: Separates automated Terraform/CI write calls from interactive human SSO sessions.

See [`aws-cloudtrail-patterns.json`](./aws-cloudtrail-patterns.json) for raw machine-readable definitions.
