# Model Benchmark Results

*Generated: 2026-01-21 02:56:20*

## System Info
- **RAM**: 31.7 GB total, 3.8 GB available
- **CPU Cores**: 20

## Results

| Model | Size | Load Time | TPS | Fact Score | Memory |
|-------|------|-----------|-----|------------|--------|
| gemma 2b it Q4_K_M | 1426MB | 1.4s | 1.2 | 43% | 2199MB |
| mistral 7b instruct v0 2 Q4_K_M | 4166MB | 2.7s | 0.8 | 86% | 4438MB |
| phi 2 Q4_K_M | 1706MB | 1.4s | 2.1 | 49% | 1997MB |
| tinyllama 1 1b chat v1 0 Q4_K_M | 638MB | 0.5s | 2.7 | 63% | 772MB |

## Analysis

- **Fastest**: tinyllama 1 1b chat v1 0 Q4_K_M (2.7 tokens/sec)
- **Most Accurate**: mistral 7b instruct v0 2 Q4_K_M (86% fact retention)
- **Most Efficient**: tinyllama 1 1b chat v1 0 Q4_K_M (772 MB)