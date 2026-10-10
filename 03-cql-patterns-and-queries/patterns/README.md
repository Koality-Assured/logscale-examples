# Domain Query Patterns Catalog

Production CQL query libraries partitioned across cloud infrastructure, identity systems, endpoint telemetry, and SaaS platforms.

## Catalog Map

| Domain | Focus Area | Target Repository | Patterns |
| :--- | :--- | :--- | :--- |
| **[AWS CloudTrail](./aws-cloudtrail/)** | Root activity, IAM mutations, security group openings | `aws-cloudtrail-logs` | [`aws-cloudtrail-patterns.json`](./aws-cloudtrail/aws-cloudtrail-patterns.json) |
| **[AWS VPC Flow](./aws-vpc-flow/)** | Port scans, external rejects, large outbound transfers | `aws-vpc-flow-logs` | [`aws-vpc-flow-patterns.json`](./aws-vpc-flow/aws-vpc-flow-patterns.json) |
| **[Okta Identity](./okta-identity/)** | Password spraying, MFA push fatigue, impossible travel | `okta-audit-logs` | [`okta-identity-patterns.json`](./okta-identity/okta-identity-patterns.json) |
| **[GitHub Audit](./github-audit/)** | Public repo leaks, org owners, deploy key creation | `github-audit-logs` | [`github-audit-patterns.json`](./github-audit/github-audit-patterns.json) |
| **[Endpoint EDR](./endpoint-edr/)** | Office spawning shells, LOLBin downloads, encoded PowerShell | `endpoint-edr-logs` | [`endpoint-edr-patterns.json`](./endpoint-edr/endpoint-edr-patterns.json) |
| **[Generative AI](./generative-ai/)** | LLM token consumption, inference latency percentiles, error spikes | `genai-telemetry-logs` | [`generative-ai-patterns.json`](./generative-ai/generative-ai-patterns.json) |
| **[Windows Security](./windows-security/)** | RDP logins (4624), user creation (4720), shadow copy deletions | `windows-event-logs` | [`windows-security-patterns.json`](./windows-security/windows-security-patterns.json) |
