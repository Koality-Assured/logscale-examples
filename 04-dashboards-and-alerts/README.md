# LogScale Dashboards, Visualizations & Alerting

Production dashboard templates (Humio dashboard schema `v0.23.0`), notification actions, and scheduled search triggers for CrowdStrike Falcon LogScale.

---

## 1. Dashboard Layout Architecture (12-Column Grid)

LogScale organizes dashboards on a 12-column responsive grid:

```
[ Col 0 | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 | Col 9 | Col 10 | Col 11 ]
[-------------------------- Note Header Banner (width: 12, height: 2) -----------------------------]
[ KPI Widget 1 (w:3) ] [ KPI Widget 2 (w:3) ] [ KPI Widget 3 (w:3) ] [ KPI Widget 4 (w:3) ]
[------------ Time Chart (width: 8, height: 5) ------------] [--- Pie Breakdown (width: 4, h: 5) ---]
[------------------------- Detailed Event Table (width: 12, height: 5) ----------------------------]
```

---

## 2. Note Widgets & Strict XML Rules

LogScale's note widget renderer accepts only a narrow HTML subset:

```yaml
note-header:
  x: 0
  y: 0
  width: 12
  height: 2
  title: Section Header
  type: note
  text: '<div style="background-color:#1e293b; color:#ffffff; padding:12px; font-weight:bold;">Section Title</div>'
```

### Critical Note Widget Rules:
- **No Query Keys**: Note widgets reject `queryString`, `visualization`, `options`, `isLive`, `start`, and `end`. Including them causes schema validation failure.
- **Div-Only Markup**: Do NOT use `<span>`, `<code>`, `<b>`, or `<strong>` inside note text. The renderer evaluates strict XML and rejects inner tags with errors like `Expected div but was code`.
- **Entity Escaping**: Always use standard XML entity escaping for ampersands (`&amp;`). Never use `&nbsp;`.

---

## 3. Parameter Chain Footgun (Existence Filters)

When configuring dashboard dropdown parameters, chaining filters:
```cql
| brand_id = ?brand | ticket_form_id = ?form | status = ?status
```
acts as an **existence filter**. Any event lacking even one of those fields (such as comment sub-events lacking `status`) will be silently excluded from the query results!

### Mitigation:
For sparsely populated fields, use conditional fallback syntax:
```cql
| (brand_id = ?brand OR ?brand = "*")
```

---

## Directory Contents

- **[`dashboards/`](./dashboards/)**: Complete YAML dashboards:
  - [`security-operations-center.yaml`](./dashboards/security-operations-center.yaml): 24h SOC command center.
  - [`aws-traffic-and-infrastructure.yaml`](./dashboards/aws-traffic-and-infrastructure.yaml): VPC Flow and ALB metrics.
  - [`identity-governance.yaml`](./dashboards/identity-governance.yaml): Okta and IAM identity health.
- **[`alerts-and-triggers/`](./alerts-and-triggers/)**:
  - [`actions/`](./alerts-and-triggers/actions/): Slack webhooks, PagerDuty integration, email templates, lookup table exporters.
  - [`triggers/`](./alerts-and-triggers/triggers/): Scheduled searches running CQL on cron intervals.
