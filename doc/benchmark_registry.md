# Due Diligence MAS — Benchmark Execution Report

## 1. Execution Overview

Six executions, 3 companies × 2 frameworks, all with `gpt-4o-mini`. All finished successfully. CrewAI figures refer to the first CrewAI version; Version 2 is still to be benchmarked.

| Company | Framework | Time (s) | LLM Calls | Total Tokens | Cost (USD) |
|---|---|---:|---:|---:|---:|
| Synthesia | CrewAI | 358.87 | 30 | 199,475 | $0.0376 |
| Synthesia | LangGraph | 173.83 | 23 | 173,057 | $0.0320 |
| ElevenLabs | CrewAI | 328.87 | 32 | 137,770 | $0.0282 |
| ElevenLabs | LangGraph | 248.61 | 28 | 166,337 | $0.0317 |
| Qdrant | CrewAI | 508.93 | 41 | 243,938 | $0.0468 |
| Qdrant | LangGraph | 314.62 | 29 | 193,755 | $0.0359 |

**Pending:** Wayve, Mistral AI and Cohere.

## 2. Comparison

| Metric | CrewAI (avg) | LangGraph (avg) | Δ |
|---|---:|---:|---|
| Time (s) | 398.89 | 245.69 | LangGraph ~38% faster |
| LLM Calls | 34.3 | 26.7 | LangGraph ~22% fewer |
| Total Tokens | 193,727 | 177,716 | LangGraph ~8% fewer |
| Cost (USD) | $0.0376 | $0.0332 | LangGraph ~12% cheaper |

Both frameworks use the same model and a similar architecture, so differences are small. LangGraph is faster and makes fewer calls, probably because of lower orchestration overhead and fewer internal retries. Cost differs by about $0.004 per run. Memo quality is equivalent. The framework choice depends mainly on developer experience, observability (LangSmith vs. CrewAI tracing) and ecosystem.
