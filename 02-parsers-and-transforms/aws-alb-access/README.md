# AWS Application Load Balancer (ALB) Access Log Parser

High-performance parser for AWS Application Load Balancer access logs.

## Parser Design Notes

- **Start-Anchored Regex**: Anchored with `^` at the beginning but intentionally lacks an end anchor (`$`). This makes the parser forward-compatible with new trailing fields introduced by AWS (such as connection trace IDs, classification reasons, or target port lists).
- **Composite IP/Port Tokens**: Captures `client` (`ip:port`) and `target` (`ip:port`) as unified tokens to prevent IPv6 colon parsing ambiguities. If separate fields are required at query time, use `splitString()`.
- **Zero Tag Cardinality**: Leaves `tagFields: []` empty. Never tag client IP addresses, trace IDs, or target URLs, as high-cardinality tags will exhaust LogScale block indexing efficiency.
