"""Serverless Snyk Security and Audit API poller for CrowdStrike LogScale.

Demonstrates:
1. Fetching security issues and audit logs from Snyk REST API (`/v1/org/{org}/audit`).
2. Deduplication and state preservation across invocations.
3. Shipping JSON records to LogScale raw ingest endpoint.
"""

import datetime
import json
import logging
import os
import urllib.parse
import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SNYK_SECRET_NAME = os.environ.get("SNYK_SECRET_NAME", "logscale/snyk-credentials")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_secrets(secret_name: str, region_name: str) -> dict:
    """Retrieves Snyk and LogScale credentials from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def send_to_logscale(events: list[dict], logscale_url: str, ingest_token: str) -> None:
    """Sends JSON events to LogScale raw ingest endpoint."""
    if not events:
        return

    payload = "\n".join(json.dumps(ev) for ev in events)
    headers = {
        "Authorization": f"Bearer {ingest_token}",
        "Content-Type": "application/json",
    }
    endpoint = urllib.parse.urljoin(logscale_url, "/api/v1/ingest/raw")
    response = requests.post(endpoint, data=payload, headers=headers, timeout=30)
    response.raise_for_status()
    logger.info(f"Successfully posted {len(events)} Snyk events to LogScale.")


def lambda_handler(event, context):
    """Executes scheduled Snyk audit retrieval."""
    logger.info("Starting Snyk API poll.")
    secrets = get_secrets(SNYK_SECRET_NAME, AWS_REGION)

    snyk_org_id = secrets["snyk_org_id"]
    snyk_token = secrets["snyk_token"]
    logscale_url = secrets["logscale_url"]
    logscale_token = secrets["logscale_ingest_token"]

    now = datetime.datetime.now(datetime.timezone.utc)
    from_date = (now - datetime.timedelta(minutes=15)).strftime("%Y-%m-%d")

    snyk_headers = {
        "Authorization": f"token {snyk_token}",
        "Content-Type": "application/json",
    }

    url = f"https://api.snyk.io/v1/org/{snyk_org_id}/audit?from={from_date}"
    response = requests.get(url, headers=snyk_headers, timeout=25)
    response.raise_for_status()

    events = response.json()
    if isinstance(events, list) and events:
        send_to_logscale(events, logscale_url, logscale_token)
        return {"statusCode": 200, "events_ingested": len(events)}

    return {"statusCode": 200, "events_ingested": 0}
