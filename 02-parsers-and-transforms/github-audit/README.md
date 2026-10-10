# GitHub Enterprise Audit Log Parser

Parses GitHub Enterprise audit log records, normalizing actor names, organization context, repository changes, and member permissions.

## Key Fields

- `Vendor.action`: GitHub audit action (e.g. `repo.create`, `org.add_member`, `repo.access_change`).
- `Vendor.actor`: GitHub handle responsible for the action.
- `Vendor.org`: GitHub organization name.
- `Vendor.repo`: Target repository full name (`org/repo`).
