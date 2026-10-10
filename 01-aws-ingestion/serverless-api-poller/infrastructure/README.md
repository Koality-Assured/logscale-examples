# Serverless Poller Infrastructure (Pulumi Python)

This Pulumi stack declaratively expands a dictionary of SaaS log sources into a resilient matrix of AWS resources:

- Lambda functions running Python 3.12 with custom memory and timeout limits.
- IAM execution roles scoped to least-privilege Secrets Manager secrets (`logscale/<product>-*`).
- EventBridge Scheduler ScheduleGroup and periodic cron rules (`rate(X minutes)`).
- SQS Dead-Letter Queues (DLQs) per product to capture unhandled invocation failures.

## Adding a Source

Edit the `api_ingest_products` dictionary in `__main__.py`:

```python
api_ingest_products = {
    "your-product": {
        "schedule_interval_minutes": 5,
        "timeout_seconds": 300,
        "memory_size": 256,
        "handler_path": "../lambdas/your-product",
        "state": "ENABLED",
    }
}
```
Then execute `pulumi up`.
