# Endpoint EDR Query Patterns

CQL detection queries for endpoint detection and response (EDR) telemetry (e.g. CrowdStrike Falcon, SentinelOne, Sysmon).

## Target Repository
- Repository: `endpoint-edr-logs`

## Key Patterns Overview

1. **Office Spawning Shell**: Classic macro and initial access attack pattern where word processors spawn command interpreters.
2. **LOLBin Downloads**: Identifies living-off-the-land binaries (`certutil.exe`, `bitsadmin.exe`) fetching remote payloads.
3. **Encoded PowerShell Execution**: Flags base64-encoded command parameters commonly used in obfuscated attack chains.

See [`endpoint-edr-patterns.json`](./endpoint-edr-patterns.json) for raw machine-readable definitions.
