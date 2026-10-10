# LogScale Scheduled Searches (Triggers)

Declarative scheduled search definitions (Humio scheduledsearch schema `v0.3.0`) that execute CQL queries on a recurring cron cadence and invoke target actions.

## Triggers Catalog

- [`scheduled-root-account-activity.yaml`](./scheduled-root-account-activity.yaml): 5-minute recurring audit evaluating AWS CloudTrail for interactive root account activity.
- [`scheduled-okta-mfa-fatigue.yaml`](./scheduled-okta-mfa-fatigue.yaml): 10-minute recurring monitor identifying >= 3 denied MFA push challenges per user.
- [`scheduled-vpc-mass-portscan.yaml`](./scheduled-vpc-mass-portscan.yaml): 15-minute scheduled search detecting horizontal network scanning against VPC firewalls.

## Key Fields

- `schedule`: Cron expression string (e.g. `*/5 * * * *`).
- `searchIntervalSeconds`: Timeframe evaluated on each run (matching or slightly exceeding schedule interval to prevent gaps).
- `actionNameReferences`: Ordered array of action names executed whenever results are returned.
