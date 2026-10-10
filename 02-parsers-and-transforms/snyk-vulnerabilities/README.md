# Snyk Vulnerability & Audit Log Parser

Parses Snyk vulnerability scan findings and administrative audit events, extracting project names, severity distributions, and critical vulnerability counts.

## Key Fields

- `Vendor.projectName`: Project or repository scanned by Snyk.
- `Vendor.packageManager`: Dependency ecosystem (`npm`, `pip`, `maven`, `go`).
- `vuln.count.critical`: Number of critical CVEs identified.
- `vuln.count.high`: Number of high CVEs identified.
