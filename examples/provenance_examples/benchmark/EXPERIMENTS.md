# Experiments and Benchmarks

## Setup
* **Dataset**: IMDB movie reviews indexed in SQLite.
* **LLM**: Local `ollama/llama3.2:3b`.
* **Hardware**: Apple M1 Pro, 16GB RAM].

## Execution Scripts
* **Benchmark Script**: `benchmark.py` (referenced as "Benchmark" in git log).
* **Mock LLM Script**: `mock_llm.py` — Used to isolate provenance overhead from LLM inference time.

## Results & Logs
Detailed performance metrics for the 10 pipelines are available in the repository:
* **CPU/Memory Logs**: Results showing that provenance tracking is significantly less resource-intensive than LLM inference.
* **Key Findings**: 
    * Provenance tracking overhead is small (+0.7% to +2.4% CPU time in most cases).
    * Using the source directly instead of wrappers keeps overhead low.
    * check the plot folder for results.
