# GitHub Enterprise Audit Log Query Patterns

Patterns for tracking code governance, developer permissions, public repository leaks, and administrative changes across GitHub organizations.

## Target Repository
- Repository: `github-audit-logs`

## Key Patterns Overview

1. **Repository Visibility Flipped to Public**: Immediate alert on accidental or unauthorized open-sourcing of private codebases.
2. **Organization Owner Grants**: Alerts on addition of organization administrators.
3. **Deploy Key Creation**: Tracks programmatic SSH key generation on repositories.

See [`github-audit-patterns.json`](./github-audit-patterns.json) for raw machine-readable definitions.
