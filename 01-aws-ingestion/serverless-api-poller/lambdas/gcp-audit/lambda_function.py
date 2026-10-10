"""Serverless GCP Cloud Audit log forwarder for CrowdStrike LogScale.

Demonstrates:
1. Connecting to Google Cloud Logging API via service account credentials stored in AWS Secrets Manager.
2. Querying Cloud Audit logs (GKE admin activity, IAM policy changes, compute instance lifecycle).
3. Normalizing and shipping structured logs into LogScale.
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

GCP_SECRET_NAME = os.environ.get("GCP_SECRET_NAME", "logscale/gcp-credentials")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_secrets(secret_name: str, region_name: str) -> dict:
    """Retrieves GCP service account credentials and LogScale tokens."""
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def send_to_logscale(entries: list[dict], logscale_url: str, ingest_token: str) -> None:
    """Posts GCP audit events to LogScale HEC endpoint."""
    if not entries:
        return

    payload = "\n".join(json.dumps({"event": entry, "sourcetype": "gcp:audit"}) for entry in entries)
    headers = {
        "Authorization": f"Bearer {ingest_token}",
        "Content-Type": "application/json",
    }
    endpoint = urllib.parse.urljoin(logscale_url, "/api/v1/ingest/hec/raw")
    response = requests.post(endpoint, data=payload, headers=headers, timeout=30)
    response.raise_for_status()
    logger.info(f"Successfully posted {len(entries)} GCP audit entries to LogScale.")


def lambda_handler(event, context):
    """Executes scheduled GCP audit log retrieval."""
    logger.info("Executing GCP Cloud Audit log collection.")
    secrets = get_secrets(GCP_SECRET_NAME, AWS_REGION)

    logscale_url = secrets["logscale_url"]
    logscale_token = secrets["logscale_ingest_token"]
    gcp_project_id = secrets["gcp_project_id"]

    # In production, query Google Cloud Logging API or consume from Pub/Sub topic subscription
    # Here we illustrate the normalized ingestion schema
    sample_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "logName": f"projects/{gcp_project_id}/logs/cloudaudit.googleapis.com%2Factivity",
        "resource": {"type": "gke_cluster", "labels": {"project_id": gcp_project_id, "cluster_name": "prod-k8s"}},
        "protoPayload": {
            "@type": "type.googleapis.com/google.cloud.audit.AuditLog",
            "serviceName": "container.googleapis.com",
            "methodName": "google.container.v1.ClusterManager.UpdateCluster",
            "authenticationInfo": {"principalEmail": "admin@example.com"},
        },
    }

    send_to_logscale([sample_entry], logscale_url, logscale_token)
    return {"statusCode": 200, "events_ingested": 1}
