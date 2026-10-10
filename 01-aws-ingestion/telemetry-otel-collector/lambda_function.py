"""OpenTelemetry (OTLP/HTTP) Ingestion Lambda for LogScale.

Receives OTLP/HTTP JSON payloads (traces, metrics, and logs) from AI coding agents,
LLM SDKs (e.g. Anthropic Claude, OpenAI, LangChain), and microservices,
unwraps typed OTLP structures into flat event dictionaries, and forwards them
to CrowdStrike Falcon LogScale.
"""

import base64
import gzip
import json
import logging
import os
import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SECRET_NAME = os.environ.get("OTEL_SECRET_NAME", "logscale/claude-otel-credentials")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

_secret_cache: dict | None = None


def get_secrets() -> dict:
    """Caches secrets in memory across warm Lambda container invocations."""
    global _secret_cache
    if _secret_cache is None:
        client = boto3.client("secretsmanager", region_name=AWS_REGION)
        raw = client.get_secret_value(SecretId=SECRET_NAME)["SecretString"]
        _secret_cache = json.loads(raw)
    return _secret_cache


def extract_value(val: dict):
    """Unwraps OTLP typed values into standard Python primitives."""
    if not val:
        return None
    if "stringValue" in val:
        return val["stringValue"]
    if "intValue" in val:
        return int(val["intValue"])
    if "doubleValue" in val:
        return float(val["doubleValue"])
    if "boolValue" in val:
        return bool(val["boolValue"])
    if "arrayValue" in val:
        return [extract_value(v) for v in val["arrayValue"].get("values", [])]
    if "kvlistValue" in val:
        return {kv["key"]: extract_value(kv["value"]) for kv in val["kvlistValue"].get("values", [])}
    return None


def extract_attributes(attributes: list) -> dict:
    """Converts an array of OTLP key-value pairs into a Python dictionary."""
    return {a["key"]: extract_value(a.get("value", {})) for a in (attributes or []) if "key" in a}


def to_timestamp_ms(val) -> int:
    """Normalizes nanosecond/millisecond epoch timestamps to milliseconds."""
    val = int(val or 0)
    if not val:
        return 0
    if val > 1_000_000_000_000_000:
        return val // 1_000_000  # nanoseconds -> milliseconds
    if val > 100_000_000_000:
        return val  # already milliseconds
    return val * 1_000  # seconds -> milliseconds


def traces_to_events(resource_spans: list) -> list[dict]:
    """Flattens OTLP resource spans into LogScale event records."""
    events = []
    for rs in resource_spans:
        resource_attrs = extract_attributes(rs.get("resource", {}).get("attributes", []))
        for ss in rs.get("scopeSpans", []):
            for span in ss.get("spans", []):
                start_ms = to_timestamp_ms(span.get("startTimeUnixNano") or 0)
                end_ms = to_timestamp_ms(span.get("endTimeUnixNano") or 0)
                event = {
                    "signal_type": "trace",
                    "trace_id": span.get("traceId", ""),
                    "span_id": span.get("spanId", ""),
                    "parent_span_id": span.get("parentSpanId", ""),
                    "span_name": span.get("name", ""),
                    "duration_ms": max(0, end_ms - start_ms),
                    "status_code": span.get("status", {}).get("code", ""),
                    "status_message": span.get("status", {}).get("message", ""),
                    "timeUnixNano": int(span.get("startTimeUnixNano") or 0),
                }
                for k, v in resource_attrs.items():
                    event[f"resource.{k}"] = v
                event.update(extract_attributes(span.get("attributes", [])))
                events.append({"attributes": event})
    return events


def logs_to_events(resource_logs: list) -> list[dict]:
    """Flattens OTLP resource logs into LogScale event records."""
    events = []
    for rl in resource_logs:
        resource_attrs = extract_attributes(rl.get("resource", {}).get("attributes", []))
        for sl in rl.get("scopeLogs", []):
            for log_record in sl.get("logRecords", []):
                event = {
                    "signal_type": "log",
                    "severity_text": log_record.get("severityText", ""),
                    "severity_number": log_record.get("severityNumber", 0),
                    "body": extract_value(log_record.get("body", {})),
                    "trace_id": log_record.get("traceId", ""),
                    "span_id": log_record.get("spanId", ""),
                }
                for k, v in resource_attrs.items():
                    event[f"resource.{k}"] = v
                event.update(extract_attributes(log_record.get("attributes", [])))
                events.append({"attributes": event})
    return events


def lambda_handler(event, context):
    """Processes incoming HTTP request from API Gateway and forwards to LogScale."""
    secrets = get_secrets()
    otlp_auth_token = secrets.get("otlp_auth_token")
    logscale_url = secrets["logscale_url"]
    logscale_token = secrets["logscale_token"]

    # Verify authorization bearer token
    req_headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    auth_header = req_headers.get("authorization", "")
    if otlp_auth_token and auth_header != f"Bearer {otlp_auth_token}":
        return {"statusCode": 401, "body": json.dumps({"error": "Unauthorized"})}

    # Handle body payload (support base64 and gzip compression)
    body = event.get("body", "")
    if event.get("isBase64Encoded", False):
        raw_bytes = base64.b64decode(body)
    else:
        raw_bytes = body.encode("utf-8")

    if req_headers.get("content-encoding") == "gzip":
        raw_bytes = gzip.decompress(raw_bytes)

    try:
        payload = json.loads(raw_bytes)
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": f"Invalid JSON: {e}"})}

    path = event.get("rawPath") or event.get("path") or ""
    logscale_events = []

    if "traces" in path or "resourceSpans" in payload:
        logscale_events = traces_to_events(payload.get("resourceSpans", []))
    elif "logs" in path or "resourceLogs" in payload:
        logscale_events = logs_to_events(payload.get("resourceLogs", []))

    if not logscale_events:
        return {"statusCode": 200, "body": json.dumps({"message": "No events to ingest"})}

    # Post to LogScale Structured Ingestion API
    logscale_endpoint = f"{logscale_url.rstrip('/')}/api/v1/ingest/humio-structured"
    ingest_payload = [{"events": logscale_events}]
    headers = {
        "Authorization": f"Bearer {logscale_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(logscale_endpoint, json=ingest_payload, headers=headers, timeout=15)
    resp.raise_for_status()

    return {
        "statusCode": 200,
        "body": json.dumps({"events_ingested": len(logscale_events)}),
    }
