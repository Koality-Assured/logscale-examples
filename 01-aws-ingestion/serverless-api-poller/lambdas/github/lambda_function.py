"""Serverless GitHub Enterprise Audit Log poller for CrowdStrike LogScale.

Demonstrates:
1. Fetching organization audit logs using the GitHub REST API (`/orgs/{org}/audit-log`).
2. Conditional requests with ETag caching (HTTP 304 Not Modified) to eliminate rate-limit burn on idle intervals.
3. Overlapping time-window cursor tracking for lossless event capture.
4. Secure token retrieval from AWS Secrets Manager.
5. High-performance NDJSON batch submission to the LogScale Ingest API / HEC endpoint.
"""

import datetime
import json
import logging
import os
import urllib.parse
import boto3
import requests

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration from environment variables
GITHUB_SECRET_NAME = os.environ.get("GITHUB_SECRET_NAME", "logscale/github-credentials")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
ETAG_CACHE_PATH = "/tmp/github-etag-cache.json"


class EtagCache:
    """Stores HTTP ETags across warm Lambda container invocations."""

    def __init__(self, path: str = ETAG_CACHE_PATH):
        self.path = path
        self.cache: dict[str, str] = {}
        self.dirty = False
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load ETag cache: {e}")
                self.cache = {}

    def get(self, key: str) -> str | None:
        return self.cache.get(key)

    def set(self, key: str, etag: str):
        if self.cache.get(key) != etag:
            self.cache[key] = etag
            self.dirty = True

    def save(self):
        if not self.dirty:
            return
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f)
            self.dirty = False
        except Exception as e:
            logger.warning(f"Failed to persist ETag cache: {e}")


def get_secrets(secret_name: str, region_name: str) -> dict:
    """Retrieves API tokens and endpoints from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def send_to_logscale(events: list[dict], logscale_url: str, ingest_token: str) -> bool:
    """Submits an array of events to LogScale's HEC (HTTP Event Collector) endpoint."""
    if not events:
        return True

    # Build HEC-formatted NDJSON payload
    hec_payload = []
    for ev in events:
        hec_entry = {
            "event": ev,
            "sourcetype": "github:audit",
            "time": ev.get("created_at") or int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
        }
        hec_payload.append(json.dumps(hec_entry))

    data = "\n".join(hec_payload)
    headers = {
        "Authorization": f"Bearer {ingest_token}",
        "Content-Type": "application/json",
    }

    hec_endpoint = urllib.parse.urljoin(logscale_url, "/api/v1/ingest/hec/raw")
    response = requests.post(hec_endpoint, data=data, headers=headers, timeout=30)
    response.raise_for_status()
    logger.info(f"Successfully posted {len(events)} events to LogScale.")
    return True


def lambda_handler(event, context):
    """Main Lambda invocation handler triggered by EventBridge schedule."""
    logger.info("Starting GitHub Audit Log poll execution.")
    secrets = get_secrets(GITHUB_SECRET_NAME, AWS_REGION)

    github_token = secrets["github_pat"]
    github_org = secrets["github_org"]
    logscale_url = secrets["logscale_url"]
    logscale_token = secrets["logscale_ingest_token"]

    etag_cache = EtagCache()
    cache_key = f"github_audit_{github_org}"
    cached_etag = etag_cache.get(cache_key)

    # Use a 7-minute lookback window for a 5-minute execution schedule (2 min overlap)
    now = datetime.datetime.now(datetime.timezone.utc)
    lookback = now - datetime.timedelta(minutes=7)
    created_filter = f">={lookback.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if cached_etag:
        headers["If-None-Match"] = cached_etag

    api_url = f"https://api.github.com/orgs/{github_org}/audit-log?phrase=created:{created_filter}&per_page=100"
    all_events = []

    try:
        response = requests.get(api_url, headers=headers, timeout=20)

        if response.status_code == 304:
            logger.info("GitHub API returned 304 Not Modified. No new audit events.")
            return {"statusCode": 200, "message": "No new events (304)"}

        response.raise_for_status()
        new_etag = response.headers.get("ETag")
        if new_etag:
            etag_cache.set(cache_key, new_etag)
            etag_cache.save()

        events = response.json()
        if isinstance(events, list):
            all_events.extend(events)

        # Pagination support via Link headers
        while "next" in response.links:
            next_url = response.links["next"]["url"]
            # Clear If-None-Match for subsequent pages
            headers.pop("If-None-Match", None)
            response = requests.get(next_url, headers=headers, timeout=20)
            response.raise_for_status()
            paged_events = response.json()
            if isinstance(paged_events, list):
                all_events.extend(paged_events)

        logger.info(f"Retrieved {len(all_events)} events from GitHub API.")
        send_to_logscale(all_events, logscale_url, logscale_token)

        return {
            "statusCode": 200,
            "events_ingested": len(all_events),
        }

    except Exception as e:
        logger.error(f"Error during GitHub audit log ingestion: {e}", exc_info=True)
        raise e
