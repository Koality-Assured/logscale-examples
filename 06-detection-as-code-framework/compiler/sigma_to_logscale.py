#!/usr/bin/env python3
"""Lightweight Sigma-to-LogScale Compiler.

Translates canonical Sigma detection YAML rules into:
1. Native CrowdStrike Falcon LogScale CQL query strings.
2. Terraform alert resources (logscale_filter_alert or logscale_aggregate_alert).
"""

import argparse
import sys
from pathlib import Path
import yaml


LOGSOURCE_TO_REPO = {
    ("aws", "cloudtrail"): "aws-cloudtrail-logs",
    ("aws", "vpc_flow"): "aws-vpc-flow-logs",
    ("okta", "system_log"): "okta-audit-logs",
    ("github", "audit_log"): "github-audit-logs",
    ("snyk", "audit"): "snyk-security-logs",
}


def compile_selection(selection: dict) -> list[str]:
    """Translates a Sigma selection dictionary into CQL filter expressions."""
    filters = []
    for field, val in selection.items():
        if isinstance(val, list):
            vals_str = ", ".join(f'"{v}"' for v in val)
            filters.append(f"in({field}, values=[{vals_str}])")
        elif isinstance(val, bool):
            filters.append(f"{field} = {str(val).lower()}")
        elif isinstance(val, (int, float)):
            filters.append(f"{field} = {val}")
        else:
            filters.append(f'{field} = "{val}"')
    return filters


def compile_sigma_rule(rule_path: Path) -> dict:
    """Parses a Sigma YAML file and produces LogScale CQL and Terraform HCL."""
    with open(rule_path, "r", encoding="utf-8") as f:
        rule = yaml.safe_load(f)

    title = rule.get("title", "Untitled Alert")
    description = rule.get("description", "")
    logsource = rule.get("logsource", {})
    product = logsource.get("product", "")
    service = logsource.get("service", "")
    repo = LOGSOURCE_TO_REPO.get((product, service), "enterprise-unified-logs-view")

    detection = rule.get("detection", {})
    selection = detection.get("selection", {})
    selection_filters = compile_selection(selection)

    base_query = f'#repo = "{repo}" ' + " ".join(selection_filters)

    aggregation = detection.get("aggregation")
    if aggregation:
        group_by = aggregation.get("groupBy", "Vendor.actor.alternateId")
        threshold = aggregation.get("threshold", 1)
        cql_query = f"{base_query} | groupBy([{group_by}], function=count(as=alert_count)) | test(alert_count >= {threshold})"
        resource_type = "logscale_aggregate_alert"
        cql_escaped = cql_query.replace('"', '\\"')
        tf_hcl = f"""resource "{resource_type}" "{rule_path.stem.replace('-', '_')}" {{
  repository_name = "{repo}"
  name            = "{title}"
  description     = "{description}"
  query_string    = "{cql_escaped}"
  enabled         = true
  throttle_time   = "{aggregation.get('timeframe', '15m')}"
}}"""
    else:
        cql_query = base_query
        cql_escaped = cql_query.replace('"', '\\"')
        resource_type = "logscale_filter_alert"
        tf_hcl = f"""resource "{resource_type}" "{rule_path.stem.replace('-', '_')}" {{
  repository_name = "{repo}"
  name            = "{title}"
  description     = "{description}"
  query_string    = "{cql_escaped}"
  enabled         = true
}}"""

    return {
        "title": title,
        "repo": repo,
        "resource_type": resource_type,
        "cql": cql_query,
        "terraform": tf_hcl,
    }


def main():
    parser = argparse.ArgumentParser(description="Compile Sigma rules to LogScale alerts.")
    parser.add_argument("rule_path", type=Path, help="Path to Sigma YAML rule file")
    args = parser.parse_args()

    if not args.rule_path.exists():
        print(f"Error: File {args.rule_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    result = compile_sigma_rule(args.rule_path)
    print("=" * 60)
    print(f" TITLE: {result['title']}")
    print(f" TARGET REPO: {result['repo']}")
    print(f" ALERT TYPE:  {result['resource_type']}")
    print("-" * 60)
    print(" GENERATED CQL:")
    print(f" {result['cql']}")
    print("-" * 60)
    print(" TERRAFORM RESOURCE:")
    print(result["terraform"])
    print("=" * 60)


if __name__ == "__main__":
    main()
