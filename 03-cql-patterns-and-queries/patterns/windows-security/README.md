# Windows Security Event Log Query Patterns

Patterns for hunting lateral movement, credential access, user account creation, and ransomware shadow copy tampering in Windows Security Event Logs.

## Target Repository
- Repository: `windows-event-logs`

## Key Patterns Overview

1. **RDP Interactive Logons (4624 / LogonType 10)**: Pinpoints remote desktop access and incoming IP origins.
2. **Account Creation (4720)**: Monitors persistence via newly minted user accounts.
3. **Volume Shadow Copy Tampering (4688)**: Detects pre-ransomware destruction commands (`vssadmin delete shadows`).

See [`windows-security-patterns.json`](./windows-security-patterns.json) for raw machine-readable definitions.
