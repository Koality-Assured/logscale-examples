# CrowdStrike Query Language (CQL / LQL) Function Reference

Comprehensive reference for CrowdStrike Falcon LogScale Query Language functions, aggregates, filters, and mathematical operators.

---

## 1. Aggregation Functions

### `groupBy`
Groups incoming events by one or more field values and evaluates aggregate functions for each group. Results are returned with synthetic aggregate columns (e.g. `_count` for `count()`).

```cql
| groupBy([aid, UserSid], function=([count(aid, as=executionCount), collect([CommandLine])]), limit=max)
```
- **Documentation**: [LogScale groupBy](https://library.humio.com/data-analysis/functions-groupby.html)

### `count`
Counts the total number of events streaming through the pipeline stage. Supports distinct counts.

```cql
| count(FileName, as=executionCount)
| count(aid, distinct=true, as=uniqueEndpoints)
```
- **Documentation**: [LogScale count](https://library.humio.com/data-analysis/functions-count.html)

### `top`
Returns the most frequent values for a given set of fields.

```cql
#event_simpleName=UserLogon UserSid=/S-1-5-21-/
| top([UserName], limit=100)
```
- **Documentation**: [LogScale top](https://library.humio.com/data-analysis/functions-top.html)

### `timeChart`
Aggregates events over time buckets, producing time-series data suitable for area, line, and bar visualizations.

```cql
| timeChart(LogonType, function=count(aid), span=1d)
```
- **Documentation**: [LogScale timeChart](https://library.humio.com/data-analysis/functions-timechart.html)

### `bucket`
Divides the search timeframe into discrete buckets generating the `_bucket` timestamp field.

```cql
| bucket(1day, field=[status], function=(count(field=userId, as="userCount")))
| _bucket := formatTime("%Y-%m-%d", field=_bucket, locale=en_US, timezone=UTC)
```
- **Documentation**: [LogScale bucket](https://library.humio.com/data-analysis/functions-bucket.html)

---

## 2. Correlation & Joins

### `selfJoinFilter`
Correlates events across different event types sharing common key fields. Prefilters during stream evaluation for optimal performance.

```cql
event_platform=Win #event_simpleName=/^(ProcessRollup2|DnsRequest)$/
| falconPID := TargetProcessId
| falconPID := ContextProcessId
| selfJoinFilter([aid, falconPID], where=[{#event_simpleName=ProcessRollup2}, {#event_simpleName=DnsRequest}], prefilter=true)
| groupBy([aid, falconPID], function=([count(#event_simpleName, distinct=true, as=eventCount), collect([ParentBaseFileName, ImageFileName, CommandLine])]))
```
- **Documentation**: [LogScale selfJoinFilter](https://library.humio.com/data-analysis/functions-selfjoinfilter.html)

### `join`
Executes an inner or left join between the primary query stream and a secondary subquery matching on a key field.

```cql
#repo = "aws-cloudtrail-logs"
| join({ #repo = "okta-audit-logs" | select([source.ip, Vendor.actor.alternateId]) }, field=source.ip, include=[Vendor.actor.alternateId], mode=left)
```
- **Documentation**: [LogScale join](https://library.humio.com/data-analysis/functions-join.html)

---

## 3. Transformation & Extraction

### `parseJson`
Extracts JSON keys into first-class query fields.

```cql
| parseJson(field=@rawstring, prefix="parsed.")
```
- **Documentation**: [LogScale parseJson](https://library.humio.com/data-analysis/functions-parsejson.html)

### `parseCsv`
Splits positional text fields separated by a delimiter into named fields.

```cql
| parseCsv(columns=["src", "dst", "port"], separator=" ")
```

### `regex`
Extracts named capture groups or validates matching against regular expressions.

```cql
| regex("user=(?<username>[^\\s]+)", field=message)
```

### `formatTime`
Formats Unix epoch milliseconds or timestamp objects into human-readable date/time strings.

```cql
| human_time := formatTime("%Y-%m-%d %H:%M:%S", field=@timestamp, timezone=UTC)
```

---

## 4. Conditional Logic & Math

### `case`
Evaluates conditions in sequential branches.

```cql
| case {
    status >= 500 => tier := "Server Error" ;
    status >= 400 => tier := "Client Error" ;
    * => tier := "Success" ;
  }
```

### `match`
Performs lookup lookups against uploaded CSV files or exact value maps.

```cql
| match(file="threat_intel_ips.csv", field=source.ip, column=ip, include=[threat_score, actor])
```

### `cidr`
Filters or tests whether an IP address resides inside a target CIDR network block.

```cql
| cidr(field=source.ip, subnet="10.0.0.0/8")
```
