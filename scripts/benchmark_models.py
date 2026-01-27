"""
Model Performance Benchmark Suite
Compares downloaded LLM models on speed, quality, and resource usage.
"""

import os
import sys
import time
import json
import argparse
import psutil
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_FILE = os.path.join(DATA_DIR, "benchmark_results.json")
RESULTS_MD = os.path.join(DATA_DIR, "benchmark_results.md")

# Test samples for consistent benchmarking
TEST_SAMPLES = [
    {
        "id": "short",
        "name": "Short Text (~100 words)",
        "text": """Machine learning is a subset of artificial intelligence that enables systems 
        to learn and improve from experience without being explicitly programmed. It focuses 
        on developing computer programs that can access data and use it to learn for themselves. 
        The process begins with observations or data, such as examples, direct experience, or 
        instruction, to look for patterns in data and make better decisions in the future.""",
        "key_concepts": ["machine learning", "artificial intelligence", "data", "patterns", "decisions"]
    },
    {
        "id": "medium", 
        "name": "Medium Text (~300 words)",
        "text": """Cloud computing is the delivery of computing services including servers, storage, 
        databases, networking, software, analytics, and intelligence over the Internet to offer 
        faster innovation, flexible resources, and economies of scale. You typically pay only for 
        cloud services you use, helping you lower your operating costs, run your infrastructure 
        more efficiently, and scale as your business needs change.
        
        Types of cloud computing include public clouds, private clouds, and hybrid clouds. Public 
        clouds are owned and operated by third-party cloud service providers, which deliver their 
        computing resources like servers and storage over the Internet. Private clouds refer to 
        cloud computing resources used exclusively by a single business or organization. A hybrid 
        cloud combines public and private clouds, bound together by technology that allows data 
        and applications to be shared between them.
        
        The main benefits of cloud computing include cost savings, increased productivity, speed 
        and efficiency, performance, reliability, and security. Organizations of every type, size, 
        and industry are using the cloud for a wide variety of use cases, such as data backup, 
        disaster recovery, email, virtual desktops, software development and testing, big data 
        analytics, and customer-facing web applications.""",
        "key_concepts": ["cloud computing", "servers", "storage", "public cloud", "private cloud", 
                        "hybrid cloud", "cost savings", "security", "scalability"]
    },
    {
        "id": "long",
        "name": "Long Text (~500 words)", 
        "text": """Natural Language Processing (NLP) is a branch of artificial intelligence that 
        helps computers understand, interpret, and manipulate human language. NLP draws from many 
        disciplines, including computer science and computational linguistics, in its pursuit to 
        fill the gap between human communication and computer understanding.
        
        NLP combines computational linguistics—rule-based modeling of human language—with statistical, 
        machine learning, and deep learning models. These technologies enable computers to process 
        human language in the form of text or voice data and to understand its full meaning, complete 
        with the speaker or writer's intent and sentiment.
        
        Common NLP tasks include speech recognition, natural language understanding, natural language 
        generation, sentiment analysis, named entity recognition, and machine translation. Speech 
        recognition converts spoken language into text. Natural language understanding helps machines 
        understand the meaning behind text. Natural language generation enables machines to produce 
        human-readable text. Sentiment analysis determines whether text expresses positive, negative, 
        or neutral sentiment.
        
        The applications of NLP are vast and growing. Virtual assistants like Siri, Alexa, and Google 
        Assistant use NLP to understand and respond to user requests. Email filters use NLP to detect 
        spam. Search engines use NLP to understand queries and retrieve relevant results. Social media 
        platforms use NLP to detect hate speech and misinformation. Healthcare providers use NLP to 
        extract information from clinical notes and medical records.
        
        Recent advances in deep learning have significantly improved NLP capabilities. Transformer 
        models like BERT and GPT have achieved state-of-the-art results on many NLP benchmarks. These 
        models are pre-trained on large amounts of text data and can be fine-tuned for specific tasks. 
        Large language models have demonstrated remarkable abilities in text generation, translation, 
        summarization, and question answering. The field continues to evolve rapidly with new research 
        pushing the boundaries of what machines can understand and generate.""",
        "key_concepts": ["NLP", "natural language processing", "machine learning", "deep learning",
                        "speech recognition", "sentiment analysis", "transformer", "BERT", "GPT",
                        "virtual assistants", "text generation", "translation"]
    }
]

TEST_QUERIES = [
    "What are the main concepts discussed?",
    "Summarize this text in 2-3 sentences.",
    "What are the key benefits mentioned?"
]


class BenchmarkResult:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model_path = ""
        self.model_size_mb = 0
        self.load_time_s = 0
        self.embedding_latency_ms = 0
        self.first_token_latency_ms = 0
        self.tokens_per_second = 0
        self.total_generation_time_s = 0
        self.peak_memory_mb = 0
        self.fact_retention_score = 0
        self.samples_tested = 0
        self.errors = []
        
    @property
    def weighted_score(self) -> float:
        """Calculate a single score for ranking (0-100)."""
        if self.errors and not self.tokens_per_second:
            return 0.0
            
        # Normalize metrics (assuming reasonable max/min values)
        # TPS: 10 is very fast for CPU, 0 is failed
        tps_norm = min(self.tokens_per_second / 10.0, 1.0) * 100
        # Accuracy: already 0-100
        accuracy_norm = self.fact_retention_score
        # Load time: 10s is slow, 0.1s is fast
        load_norm = max(0, (10.0 - min(self.load_time_s, 10.0)) / 10.0) * 100
        # Memory: 8GB is high, 0.5GB is low (for these models)
        mem_norm = max(0, (8192.0 - min(self.peak_memory_mb, 8192.0)) / 8192.0) * 100
        
        # Weights
        return (tps_norm * 0.45) + (accuracy_norm * 0.45) + (load_norm * 0.05) + (mem_norm * 0.05)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "model_size_mb": round(self.model_size_mb, 2),
            "load_time_s": round(self.load_time_s, 2),
            "embedding_latency_ms": round(self.embedding_latency_ms, 2),
            "first_token_latency_ms": round(self.first_token_latency_ms, 2),
            "tokens_per_second": round(self.tokens_per_second, 2),
            "total_generation_time_s": round(self.total_generation_time_s, 2),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "fact_retention_score": round(self.fact_retention_score, 2),
            "weighted_score": round(self.weighted_score, 2),
            "samples_tested": self.samples_tested,
            "errors": self.errors
        }
        return d


def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def calculate_fact_retention(summary: str, key_concepts: List[str]) -> float:
    """Calculate what percentage of key concepts appear in the summary, with basic noise filtering."""
    if not summary or not key_concepts:
        return 0.0
    
    import re
    summary_clean = re.sub(r'[^\w\s]', '', summary.lower())
    
    found = 0
    for concept in key_concepts:
        concept_lower = concept.lower()
        # Look for exact word match or substring if multiple words
        if concept_lower in summary_clean:
            found += 1
            
    return (found / len(key_concepts)) * 100


def get_local_models() -> List[Dict[str, Any]]:
    """Get list of downloaded models."""
    models = []
    if os.path.exists(MODELS_DIR):
        for f in os.listdir(MODELS_DIR):
            if f.endswith(".gguf"):
                filepath = os.path.join(MODELS_DIR, f)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                models.append({
                    "name": f.replace(".gguf", "").replace("-", " ").replace(".", " "),
                    "filename": f,
                    "path": os.path.abspath(filepath),
                    "size_mb": size_mb
                })
    return models


def benchmark_model(model_info: Dict[str, Any], verbose: bool = True) -> BenchmarkResult:
    """Run benchmark suite on a single model."""
    result = BenchmarkResult(model_info["name"])
    result.model_path = model_info["path"]
    result.model_size_mb = model_info["size_mb"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Benchmarking: {model_info['name']}")
        print(f"Size: {model_info['size_mb']:.2f} MB")
        print(f"{'='*60}")
    
    try:
        from backend.llm_integration import get_embeddings, summarize
        from langchain_community.llms import LlamaCpp
        
        baseline_memory = get_memory_usage_mb()
        
        # Load model and measure time
        if verbose:
            print("Loading model...")
        load_start = time.time()
        
        llm = LlamaCpp(
            model_path=model_info["path"],
            n_ctx=2048,
            n_batch=512,
            verbose=False
        )
        
        result.load_time_s = time.time() - load_start
        if verbose:
            print(f"  Load time: {result.load_time_s:.2f}s")
        
        # Warmup run
        if verbose:
            print("Warmup run...")
        _ = llm.invoke("Hello")
        
        # Benchmark embedding (using local embeddings)
        if verbose:
            print("Testing embedding latency...")
        embeddings = get_embeddings("local", None, model_info["path"])
        embed_start = time.time()
        _ = embeddings.embed_query("Test query for embedding speed measurement")
        result.embedding_latency_ms = (time.time() - embed_start) * 1000
        if verbose:
            print(f"  Embedding latency: {result.embedding_latency_ms:.2f}ms")
        
        # Benchmark generation
        total_tokens = 0
        total_time = 0
        first_token_times = []
        fact_scores = []
        
        for sample in TEST_SAMPLES:
            if verbose:
                print(f"Testing: {sample['name']}...")
            
            prompt = f"Summarize this text concisely:\n\n{sample['text']}\n\nSummary:"
            
            # Measure first token and total generation
            gen_start = time.time()
            response = llm.invoke(prompt)
            gen_time = time.time() - gen_start
            
            if response:
                tokens = len(response.split())
                total_tokens += tokens
                total_time += gen_time
                
                # Estimate first token latency (approximation)
                first_token_times.append(gen_time / max(tokens, 1))
                
                # Calculate fact retention
                fact_score = calculate_fact_retention(response, sample["key_concepts"])
                fact_scores.append(fact_score)
                
                if verbose:
                    print(f"    Generated {tokens} tokens in {gen_time:.2f}s")
                    print(f"    Fact retention: {fact_score:.1f}%")
            
            result.samples_tested += 1
        
        # Calculate aggregates
        if total_time > 0:
            result.tokens_per_second = total_tokens / total_time
        if first_token_times:
            result.first_token_latency_ms = (sum(first_token_times) / len(first_token_times)) * 1000
        if fact_scores:
            result.fact_retention_score = sum(fact_scores) / len(fact_scores)
        result.total_generation_time_s = total_time
        
        # Measure peak memory
        result.peak_memory_mb = get_memory_usage_mb() - baseline_memory
        
        if verbose:
            print(f"\nResults for {model_info['name']}:")
            print(f"  Tokens/sec: {result.tokens_per_second:.2f}")
            print(f"  Avg fact retention: {result.fact_retention_score:.1f}%")
            print(f"  Memory used: {result.peak_memory_mb:.2f} MB")
        
    except Exception as e:
        result.errors.append(str(e))
        if verbose:
            print(f"  ERROR: {e}")
    
    return result


def run_all_benchmarks(verbose: bool = True) -> List[BenchmarkResult]:
    """Run benchmarks on all downloaded models."""
    models = get_local_models()
    
    if not models:
        print("No models found in 'models/' directory.")
        print("Please download a model first using the Model Manager in the UI.")
        return []
    
    print(f"\nFound {len(models)} model(s) to benchmark:")
    for m in models:
        print(f"  - {m['name']} ({m['size_mb']:.2f} MB)")
    
    results = []
    for model in models:
        result = benchmark_model(model, verbose)
        results.append(result)
    
    return results


def save_results(results: List[BenchmarkResult]):
    """Save results to JSON and Markdown files."""
    # JSON output
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "total_ram_gb": psutil.virtual_memory().total / (1024**3),
            "available_ram_gb": psutil.virtual_memory().available / (1024**3),
            "cpu_count": psutil.cpu_count()
        },
        "results": [r.to_dict() for r in results]
    }
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    # Markdown output
    md_lines = [
        "# Model Benchmark Results",
        f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "## System Info",
        f"- **RAM**: {json_data['system_info']['total_ram_gb']:.1f} GB total, "
        f"{json_data['system_info']['available_ram_gb']:.1f} GB available",
        f"- **CPU Cores**: {json_data['system_info']['cpu_count']}\n",
        "## Results\n",
        "| Model | Size | Load Time | TPS | Fact Score | Memory |",
        "|-------|------|-----------|-----|------------|--------|"
    ]
    
    for r in results:
        md_lines.append(
            f"| {r.model_name} | {r.model_size_mb:.0f}MB | {r.load_time_s:.1f}s | "
            f"{r.tokens_per_second:.1f} | {r.fact_retention_score:.0f}% | {r.peak_memory_mb:.0f}MB |"
        )
    
    # Winner analysis
    if results:
        md_lines.append("\n## Analysis\n")
        
        fastest = max(results, key=lambda r: r.tokens_per_second)
        most_accurate = max(results, key=lambda r: r.fact_retention_score)
        most_efficient = min(results, key=lambda r: r.peak_memory_mb if r.peak_memory_mb > 0 else float('inf'))
        
        md_lines.append(f"- **Fastest**: {fastest.model_name} ({fastest.tokens_per_second:.1f} tokens/sec)")
        md_lines.append(f"- **Most Accurate**: {most_accurate.model_name} ({most_accurate.fact_retention_score:.0f}% fact retention)")
        md_lines.append(f"- **Most Efficient**: {most_efficient.model_name} ({most_efficient.peak_memory_mb:.0f} MB)")
    
    with open(RESULTS_MD, 'w') as f:
        f.write('\n'.join(md_lines))
    
    print(f"\nResults saved to:")
    print(f"  - {RESULTS_FILE}")
    print(f"  - {RESULTS_MD}")


def print_summary(results: List[BenchmarkResult]):
    """Print a summary table to console."""
    print("\n" + "="*80)
    print(" BENCHMARK SUMMARY")
    print("="*80)
    print(f"{'Model':<35} {'Size':>8} {'TPS':>8} {'Fact%':>8} {'Memory':>10}")
    print("-"*80)
    
    for r in results:
        print(f"{r.model_name:<35} {r.model_size_mb:>6.0f}MB {r.tokens_per_second:>8.1f} "
              f"{r.fact_retention_score:>7.0f}% {r.peak_memory_mb:>8.0f}MB")
    
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description="Benchmark LLM models")
    parser.add_argument("--all", action="store_true", help="Benchmark all downloaded models")
    parser.add_argument("--model", type=str, help="Benchmark a specific model by filename")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print(" FILE SEARCH ENGINE - Model Benchmarking Suite")
    print("="*60)
    
    if args.model:
        model_path = os.path.join(MODELS_DIR, args.model)
        if not os.path.exists(model_path):
            print(f"Model not found: {model_path}")
            sys.exit(1)
        models = [{
            "name": args.model.replace(".gguf", ""),
            "filename": args.model,
            "path": os.path.abspath(model_path),
            "size_mb": os.path.getsize(model_path) / (1024 * 1024)
        }]
        results = [benchmark_model(m, not args.quiet) for m in models]
    else:
        results = run_all_benchmarks(not args.quiet)
    
    if results:
        save_results(results)
        print_summary(results)
    
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
