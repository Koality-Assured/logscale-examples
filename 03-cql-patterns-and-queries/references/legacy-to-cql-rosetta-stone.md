# Splunk SPL & Elasticsearch DSL → LogScale CQL Rosetta Stone

Comprehensive command-by-command migration guide for translating Splunk Search Processing Language (SPL) and Elasticsearch DSL into CrowdStrike Query Language (CQL / LQL).

---

## Command Quick Reference

| Operation | Legacy Splunk SPL | LogScale CQL Equivalent | Critical Notes & Caveats |
| :--- | :--- | :--- | :--- |
| **Time Bucketing** | `\| bucket _time span=1d` | `\| bucket(1d, ...)` | Emits synthetic `_bucket` timestamp field |
| **First Non-Null** | `\| eval x=coalesce(a, b)`| `\| x := concat([a, b])` or chain `:=` | `concat()` returns first populated string |
| **Format Time** | `\| convert ctime(_time)` | `\| formatTime("%Y-%m-%d", ...)` | Formats epoch milliseconds into strings |
| **Deduplication** | `\| dedup host, user` | `\| groupBy([host, user], function=selectLast())` | LogScale has no raw `dedup`; use `groupBy` |
| **Field Assignment**| `\| eval speed=dist/time` | `\| speed := dist / time` | Uses `:=` syntax for assignment |
| **Field Projection**| `\| fields host, ip, user` | `\| select([host, ip, user])` | Drops all unlisted fields |
| **Default Value** | `\| fillnull value="-" x` | `\| default(field=x, value="-")` | Replaces null/empty attributes |
| **Newest Events** | `\| head 10` | `\| tail(10)` | **REVERSED**: Splunk `head` = newest; CQL `tail` = newest |
| **Oldest Events** | `\| tail 10` | `\| head(10)` | **REVERSED**: Splunk `tail` = oldest; CQL `head` = oldest |
| **Value Inclusion**| `\| where x IN ("a", "b")`| `\| in(x, values=["a", "b"])` | `in()` is a pipe-stage filter |
| **Read Lookup** | `\| inputlookup my_ips.csv`| `\| readFile("my_ips.csv")` | Reads uploaded lookup table into stream |
| **GeoIP Lookup** | `\| iplocation client_ip` | `\| ipLocation(client_ip)` | Enriches with city, country, coordinates |
| **Subquery Join** | `\| join user [search ...]`| `\| join({ ... }, field=user)` | Subquery join on matching keys |
| **Enrich Lookup** | `\| lookup users.csv id OUTPUT name` | `\| match(file="users.csv", field=id, column=id, include=[name])` | Inlines CSV data |
| **Split Multi-Val**| `\| makemv delim="," tags`| `\| splitString(field=tags, by=",")` | Converts delimited string into array |
| **Create Sample** | `\| makeresults` | `\| createEvents(count=1)` | Generates synthetic testing events |
| **Regex Match** | `\| rex field=msg "(?<id>\d+)"` | `\| regex("(?<id>\d+)", field=msg)` | Extracts named groups |
| **Rename Field** | `\| rename src_ip AS clientIp`| `\| clientIp := src_ip \| drop(src_ip)` or `\| rename(field=src_ip, as=clientIp)` | Renames field identifier |
| **Sort Order** | `\| sort -_time, +user` | `\| sort(field=@timestamp, order=desc)` | Explicit sort ordering |
| **JSON Extract** | `\| spath input=raw_json` | `\| parseJson(field=raw_json)` | Extracts nested JSON structures |
| **Aggregation** | `\| stats count, dc(ip) by host`| `\| groupBy([host], function=([count(), count(ip, distinct=true)]))` | Multi-metric grouping |
| **Time Series** | `\| timechart span=1h count by code` | `\| timeChart(code, span=1h)` | Generates time-series buckets |
| **Top Values** | `\| top limit=10 username` | `\| top([username], limit=10)` | Fast frequency ranking |
| **Boolean Filter** | `\| where status > 400` | `\| test(status > 400)` or direct pipe `\| status > 400` | Evaluates boolean expression |

---

## Detailed Transformation Examples

### 1. Grouping & Distinct Counting (`stats` → `groupBy`)

**Splunk SPL:**
```spl
index=aws_cloudtrail
| stats count as total_calls, dc(eventName) as distinct_actions by userIdentity.principalId
| where total_calls > 100
| sort - total_calls
```

**LogScale CQL:**
```cql
#repo = "aws-cloudtrail-logs"
| groupBy([Vendor.userIdentity.principalId], function=([
    count(as=total_calls),
    count(Vendor.eventName, distinct=true, as=distinct_actions)
  ]))
| total_calls > 100
| sort(field=total_calls, order=desc)
```

---

### 2. Stream Deduplication (`dedup` → `groupBy` + `selectLast`)

LogScale streams events continuously without loading entire historical sets into random-access buffers. To achieve `dedup` semantics:

**Splunk SPL:**
```spl
index=okta
| dedup actor.alternateId
```

**LogScale CQL:**
```cql
#repo = "okta-audit-logs"
| groupBy([Vendor.actor.alternateId], function=selectLast([@timestamp, source.ip, Vendor.eventType]))
```

---

### 3. Conditional Classification (`eval case` → `case{}`)

**Splunk SPL:**
```spl
| eval risk_tier=case(score>=90, "CRITICAL", score>=70, "HIGH", score>=40, "MEDIUM", true(), "LOW")
```

**LogScale CQL:**
```cql
| case {
    score >= 90 => risk_tier := "CRITICAL" ;
    score >= 70 => risk_tier := "HIGH" ;
    score >= 40 => risk_tier := "MEDIUM" ;
    * => risk_tier := "LOW" ;
  }
```

---

### 4. Head vs Tail Orientation (Critical Inversion!)

In Splunk SPL, searches return results descending by time (`_time`), so `| head 5` returns the **newest** 5 events, while `| tail 5` returns the **oldest** 5 events.

In LogScale CQL, events stream in chronological order from past to present:
- `| tail(5)` returns the **latest / newest** 5 events (the tail of the incoming stream).
- `| head(5)` returns the **earliest / oldest** 5 events (the head of the stream).
