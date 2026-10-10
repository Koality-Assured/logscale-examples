"""Serverless Okta System Log API poller for CrowdStrike LogScale.

Demonstrates:
1. Polling Okta's System Log API (`/api/v1/logs`) using ISO 8601 timestamps.
2. Handling RFC 5988 HTTP `Link` headers with `rel="next"` for reliable cursor pagination.
3. Batching events and submitting structured JSON payloads to LogScale's `/api/v1/ingest/raw` endpoint.
4. Resilient error handling and exponential backoff on HTTP 429 (Rate Limit).
"""

import datetime
import json
import logging
import os
import time
import urllib.parse
import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

OKTA_SECRET_NAME = os.environ.get("OKTA_SECRET_NAME", "logscale/okta-credentials")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_secrets(secret_name: str, region_name: str) -> dict:
    """Fetches Okta and LogScale tokens from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def send_to_logscale(events: list[dict], logscale_url: str, ingest_token: str) -> None:
    """Posts log events to LogScale's structured ingest API."""
    if not events:
        return

    # Prepare LogScale batch payload format
    payload = [
        {
            "tags": {"host": "okta", "source": "okta-system-log"},
            "events": [
                {
                    "timestamp": ev.get("published"),
                    "attributes": ev,
                }
                for ev in events
            ],
        }
    ]

    endpoint = urllib.parse.urljoin(logscale_url, "/api/v1/ingest/humio-structured")
    headers = {
        "Authorization": f"Bearer {ingest_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    logger.info(f"Pushed {len(events)} Okta events to LogScale.")


def lambda_handler(event, context):
    """Executes scheduled Okta log retrieval."""
    logger.info("Initiating Okta System Log poll.")
    secrets = get_secrets(OKTA_SECRET_NAME, AWS_REGION)

    okta_domain = secrets["okta_domain"]  # e.g., "example.okta.com"
    okta_api_token = secrets["okta_api_token"]
    logscale_url = secrets["logscale_url"]
    logscale_token = secrets["logscale_ingest_token"]

    # Calculate polling time window (last 3 minutes with 1 minute overlap for a 2-minute cron)
    now = datetime.datetime.now(datetime.timezone.utc)
    since_time = (now - datetime.timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%SZ")

    okta_headers = {
        "Accept": "application/json",
        "Authorization": f"SSWS {okta_api_token}",
    }

    url = f"https://{okta_domain}/api/v1/logs?since={since_time}&limit=100"
    total_events = 0
    max_pages = 50

    try:
        page_count = 0
        while url and page_count < max_pages:
            page_count += 1
            response = requests.get(url, headers=okta_headers, timeout=20)

            # Handle Okta Rate Limiting
            if response.status_code == 429:
                reset_epoch = int(response.headers.get("X-Rate-Limit-Reset", 0))
                sleep_sec = max(1, reset_epoch - int(time.time()))
                logger.warning(f"Rate limited by Okta API. Sleeping {sleep_sec}s.")
                time.sleep(sleep_sec)
                continue

            response.raise_for_status()
            batch = response.json()

            if batch and isinstance(batch, list):
                total_events += len(batch)
                send_to_logscale(batch, logscale_url, logscale_token)

            # Follow cursor pagination
            next_link = response.links.get("next")
            if next_link and next_link.get("url"):
                # Stop if next page is identical to current or if batch is empty
                if next_link["url"] == url or not batch:
                    break
                url = next_link["url"]
            else:
                break

        logger.info(f"Finished Okta poll: {total_events} total events ingested across {page_count} pages.")
        return {"statusCode": 200, "events_ingested": total_events}

    except Exception as e:
        logger.error(f"Failed to poll Okta System Log: {e}", exc_info=True)
        raise e
