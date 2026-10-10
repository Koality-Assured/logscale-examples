# LogScale Actions

Reusable action templates (Humio action schema `v0.10.0`) defining outbound notification destinations and lookup file maintenance jobs.

## Files

- [`slack-incoming-webhook.yaml`](./slack-incoming-webhook.yaml): Posts markdown-formatted alerts to Slack channels via incoming webhooks.
- [`pagerduty-incident-webhook.yaml`](./pagerduty-incident-webhook.yaml): Triggers high-priority incidents in PagerDuty via the Events API v2.
- [`email-security-notification.yaml`](./email-security-notification.yaml): Formats plain-text email alerts and automatically attaches query result CSV files.
- [`upload-threat-lookup.yaml`](./upload-threat-lookup.yaml): Overwrites an in-repository CSV lookup file (`threat_intel_ips.csv`) with the results of a scheduled aggregation query.
