# Okta Identity Query Patterns

Validated CQL patterns for detecting credential stuffing, password spraying, MFA fatigue attacks, and anomalous geographic logins in Okta System Logs.

## Target Repository
- Repository: `okta-audit-logs`

## Key Patterns Overview

1. **Password Spray / Brute Force**: Detects single IPs attempting logins across multiple distinct employee email accounts.
2. **MFA Push Fatigue**: Identifies repeated push denial events (`outcome.result = DENY`) within a short timeframe.
3. **Admin Privilege Grants**: Audits role elevation and sensitive group assignments in Okta.
4. **Impossible Travel Anomaly**: Surfaces accounts authenticating from multiple countries within a narrow time window.

See [`okta-identity-patterns.json`](./okta-identity-patterns.json) for raw machine-readable definitions.
