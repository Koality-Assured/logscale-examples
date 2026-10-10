# Repository AGENTS

Canonical rules for AI agents operating within `Koality-Assured/logscale-examples`.

## Scope & Purpose
This repository provides production-grade, generalized, secure architectural patterns, parser definitions, CrowdStrike Query Language (CQL / LQL) references, dashboard blueprints, AWS ingestion pipelines, and Terraform configurations for [CrowdStrike Falcon LogScale](https://www.crowdstrike.com/products/next-gen-siem/falcon-logscale/) (formerly Humio).

It serves as an authoritative open-source reference for engineering and security teams designing resilient log ingestion, high-performance parsers, detection-as-code pipelines, and observability dashboards.

## Non-Negotiable Directives

### 1. Sanitization & Public Hygiene (CRITICAL)
- **Zero Secrets / Internal Identifiers**: NEVER commit or hardcode private credentials, API keys, internal company names (legacy corporate entities, subsidiaries, proprietary code names), internal employee names, internal URLs, or real AWS/GCP account numbers.
- **Forbidden Identifier Check**: All code and documentation must strictly pass `adversarial_review.py` with zero forbidden terms.
- **Synthetic Placeholders**: Use obvious synthetic placeholders (`123456789012`, `example.com`, `sample-org`, `us-west-2a`, `arn:aws:iam::123456789012:role/SampleRole`).
- **Standard Third-Party Identifiers**: Public vendor accounts such as CrowdStrike's standard ingest account (`426876924399`) are allowed only when explicitly documented in vendor setup guides.

### 2. Example-Only Scope (NO Real Execution)
- **No Live GitHub Actions**: Do NOT create real `.github/workflows/` runner pipelines that execute against cloud providers. CI/CD integration patterns must be documented in Markdown or sample non-executing templates.
- **No Live Cloud Deployments**: Do NOT invoke `pulumi up` or `terraform apply` against live cloud environments from this repository. All manifests, scripts, and programs must be syntactically valid and structurally complete for reference and testing.

### 3. Progressive Navigation & Structure
- Examples are partitioned into six dedicated domains:
  1. `01-aws-ingestion/` (S3-SQS pull feeds, serverless API pollers, OpenTelemetry forwarders)
  2. `02-parsers-and-transforms/` (Production parser definitions, Grok/Regex/LQL transforms, test cases)
  3. `03-cql-patterns-and-queries/` (CQL function reference, technique guides, SPL-to-CQL Rosetta Stone, pattern catalog)
  4. `04-dashboards-and-alerts/` (Declarative YAML dashboards, alerts, triggers, actions)
  5. `05-terraform-logscale-management/` (Terraform modules and deployment blueprints for LogScale resources)
  6. `06-detection-as-code-framework/` (Sigma rule repository, compilation pipeline, automated alert sync)
- Every subdirectory must maintain an informative `README.md` explaining architecture, design tradeoffs, inputs, and outputs.

### 4. Adversarial Review Standard
- Before merging any branch into `main`, `python adversarial_review.py` must execute cleanly with zero warnings or failures.
