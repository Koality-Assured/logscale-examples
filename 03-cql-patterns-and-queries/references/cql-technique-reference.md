# CrowdStrike Query Language (CQL) Advanced Technique Reference

Design patterns and idioms for advanced security analytics, high-speed correlations, sessionization, and anomaly detection in LogScale.

---

## 1. Predicate Pushdown & Filter-First Architecture

LogScale is a streaming engine designed to process gigabytes of data per second per core. However, streaming speed depends directly on how many events reach the pipe (`|`) operators.

### Rule: Always filter before the first pipe!

```cql
// SLOW (Anti-Pattern): Full scan through pipe filter
#repo = "aws-cloudtrail-logs"
| Vendor.eventName = "ConsoleLogin"
| groupBy([Vendor.userIdentity.principalId])

// FAST (Best Practice): Pushed into initial scan filter
#repo = "aws-cloudtrail-logs" Vendor.eventName = "ConsoleLogin"
| groupBy([Vendor.userIdentity.principalId])
```
Filtering in the initial search expression allows LogScale's block indexers to skip entire storage blocks that do not contain matching tokens.

---

## 2. Sessionization Across Disjoint Telemetry

When tracking an identity across multiple SaaS platforms and cloud providers, use sessionization queries to stitch events together by IP and timestamp proximity:

```cql
(#repo = "okta-audit-logs" OR #repo = "aws-cloudtrail-logs")
| ip := concat([source.ip, Vendor.sourceIPAddress])
| user := concat([Vendor.actor.alternateId, Vendor.userIdentity.principalId])
| groupBy([ip], function=([
    collect([user]),
    count(as=action_count),
    min(@timestamp, as=first_seen),
    max(@timestamp, as=last_seen)
  ]))
| session_duration_sec := (last_seen - first_seen) / 1000
| sort(field=action_count, order=desc)
```

---

## 3. Transaction Duration & Latency Measurement

Measure the time elapsed between start and end operations using `selectLast` and `selectFirst` within a `groupBy`:

```cql
#event_simpleName = /^(TaskStarted|TaskCompleted)$/
| groupBy([task_id], function=([
    selectFirst([@timestamp, status], as=[start_time, initial_status]),
    selectLast([@timestamp, status], as=[end_time, final_status])
  ]))
| duration_ms := end_time - start_time
| test(duration_ms > 5000)
| sort(field=duration_ms, order=desc)
```

---

## 4. IP CIDR Filtering & Private Subnet Exclusion

Isolate external traffic by filtering out RFC 1918 private subnets:

```cql
#repo = "aws-vpc-flow-logs" #action = "REJECT"
| test(!cidr(field=srcaddr, subnet="10.0.0.0/8"))
| test(!cidr(field=srcaddr, subnet="172.16.0.0/12"))
| test(!cidr(field=srcaddr, subnet="192.168.0.0/16"))
| top([srcaddr, dstport], limit=25)
```

---

## 5. Anomaly Detection via Sliding Baselines

Compare current 1-hour activity against a 24-hour historical baseline:

```cql
#repo = "aws-cloudtrail-logs" Vendor.readOnly = false
| bucket(1h, field=[Vendor.eventName], function=count(as=hourly_writes))
| window(hourly_writes, sliding=24, function=([
    avg(hourly_writes, as=rolling_avg),
    stdDev(hourly_writes, as=rolling_stddev)
  ]))
| z_score := (hourly_writes - rolling_avg) / rolling_stddev
| test(z_score > 3.0)
```
