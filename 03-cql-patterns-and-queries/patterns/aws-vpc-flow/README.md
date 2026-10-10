# AWS VPC Flow Log Query Patterns

High-performance CQL patterns for monitoring network throughput, investigating ingress port scanning, and identifying high-volume outbound data exfiltration attempts.

## Target Repository
- Repository: `aws-vpc-flow-logs`

## Key Patterns Overview

1. **Rejected External Ingress**: Uses `cidr()` to exclude RFC 1918 private subnets and rank external IPs hammering firewall ports.
2. **Horizontal Port Scan Detection**: Groups by `srcaddr` and triggers when a single origin contacts >= 20 distinct destination ports.
3. **Large Outbound Egress Anomalies**: Identifies high-bandwidth sessions transferring >100MB outside the corporate cloud perimeter.

See [`aws-vpc-flow-patterns.json`](./aws-vpc-flow-patterns.json) for raw machine-readable definitions.
