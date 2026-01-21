# Model Benchmark Results

*Generated: 2026-01-22 02:54:34*

## System Info
- **RAM**: 31.7 GB total, 15.1 GB available
- **CPU Cores**: 20

## Results

| Model | Size | Load Time | TPS | Fact Score | Memory |
|-------|------|-----------|-----|------------|--------|
| gemma 2b it Q4_K_M | 1426MB | 0.5s | 4.1 | 41% | 1967MB |
| mistral 7b instruct v0 2 Q4_K_M | 4166MB | 0.7s | 3.0 | 87% | 4518MB |
| Mistral 7B Instruct v0 3 Q8_0 | 7346MB | 1.7s | 2.3 | 79% | 7627MB |
| phi 2 Q4_K_M | 1706MB | 0.6s | 7.0 | 71% | 2469MB |
| tinyllama 1 1b chat v1 0 Q4_K_M | 638MB | 0.2s | 15.4 | 39% | 767MB |

## Analysis

- **Fastest**: tinyllama 1 1b chat v1 0 Q4_K_M (15.4 tokens/sec)
- **Most Accurate**: mistral 7b instruct v0 2 Q4_K_M (87% fact retention)
- **Most Efficient**: tinyllama 1 1b chat v1 0 Q4_K_M (767 MB)