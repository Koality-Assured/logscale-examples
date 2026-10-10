# Generative AI Observability Query Patterns

Patterns for tracking LLM inference cost, token velocity, prompt latency percentiles, and provider error spikes in LogScale.

## Target Repository
- Repository: `genai-telemetry-logs`

## Key Patterns Overview

1. **Token Usage Accounting**: Sums prompt and completion tokens across developer teams and foundation models.
2. **Inference Latency Percentiles**: Calculates P50, P90, and P99 response times using `percentile()`.
3. **Model Error Spikes**: Flags rate-limiting (429) and upstream provider downtime (503).

See [`generative-ai-patterns.json`](./generative-ai-patterns.json) for raw machine-readable definitions.
