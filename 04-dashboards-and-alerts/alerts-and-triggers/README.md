# Alerts, Actions & Triggers

This subdirectory contains modular LogScale alerting configurations split into **actions** (notification destinations) and **triggers** (scheduled CQL search queries).

## Subdirectories

- **[`actions/`](./actions/)**: Outbound notification channels (Slack webhooks, PagerDuty incident generation, email templates, lookup table CSV updates).
- **[`triggers/`](./triggers/)**: Cron-scheduled searches that evaluate CQL queries and dispatch alerts to referenced actions.
