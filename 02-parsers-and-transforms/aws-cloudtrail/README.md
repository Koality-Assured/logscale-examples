# AWS CloudTrail JSON Parser

Normalizes multi-field AWS CloudTrail audit records into Elastic Common Schema (ECS) and Vendor-prefixed naming conventions.

## Field Normalization Map

| CloudTrail Native Field | Normalized Field | Purpose |
| :--- | :--- | :--- |
| `eventTime` | `@timestamp` | Primary event timestamp |
| `eventSource` | `Vendor.eventSource` | Target AWS service (`iam.amazonaws.com`, `s3.amazonaws.com`) |
| `eventName` | `Vendor.eventName` | AWS action name (`CreatePolicy`, `PutBucketPolicy`) |
| `userIdentity.principalId` | `Vendor.userIdentity.principalId` | Best field for pinpointing human SSO identities |
| `userIdentity.sessionContext.sessionIssuer.userName` | `Vendor.userIdentity.sessionIssuer` | Underlying IAM role assumed during the session |
| `recipientAccountId` | `cloud.account.id` | Target AWS 12-digit account identifier |
| `awsRegion` | `cloud.region` | Regional location of the event |
