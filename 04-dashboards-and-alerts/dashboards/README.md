# LogScale Declarative Dashboards

Production dashboard templates using the official Humio dashboard schema (`v0.23.0`).

## Dashboards Catalog

- [`security-operations-center.yaml`](./security-operations-center.yaml): 24-hour SOC command center tracking root logins, Okta failure spikes, rejected network flows, and CloudTrail administrative mutations.
- [`aws-traffic-and-infrastructure.yaml`](./aws-traffic-and-infrastructure.yaml): Network operations dashboard visualizing VPC flow bandwidth, ALB 5XX error rates, and target latency percentiles.
- [`identity-governance.yaml`](./identity-governance.yaml): Okta and IAM identity posture dashboard tracking active SSO users, MFA challenge volumes, top applications, and geographic access distributions.

## How to Import

In LogScale:
1. Navigate to your target repository or view.
2. Select **Dashboards > New Dashboard > Import Dashboard from YAML**.
3. Upload any `.yaml` file from this directory.
