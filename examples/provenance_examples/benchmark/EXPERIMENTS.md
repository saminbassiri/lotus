# Experiments and Benchmarks

## Setup
* **Dataset**: IMDB movie reviews indexed in SQLite.
* **LLM**: Local `ollama/llama3.2:3b`.
* **Hardware**: Apple M1 Pro, 32GB RAM].

## Execution Scripts
* **Benchmark Script**: `benchmark.py` (referenced as "Benchmark" in git log).
* **Mock LLM Script**: `mock_llm.py` — Used to isolate provenance overhead from LLM inference time.

## Results & Logs
Detailed performance metrics for the 10 pipelines are available in the repository under: `results/raw_data/`
Plots can be found in `results/plots/`.
* **CPU/Memory Logs**: Results showing that provenance tracking is significantly less resource-intensive than LLM inference.
* **Key Findings**: 
    * Provenance tracking overhead is relatively small in memory but also in CPU time compared to LLM inference.
      * with approx. +10.9% on average for CPU time (ranging from +0.1% to max. +33.7% )
      * +3.4% on average for memory usage (ranging from + 0.1% to max. +15.6%)
    * Using the source directly instead of wrappers keeps overhead low.
    * check the plot and benchmark log folder for results.
* **Contraints**: 
    * the dataset is limited to 100 records, in the `results/plots/` folder, more plots for 200 record size data can be found aswell
    * the original dataset contains 50k movie reviews (`/../examples/data/`). We limit the `review` text to a maximum of 200 characters as a cost tradeoff
    * we ensured a consistent environment for all exmperiments (single machine, mocked LM, etc.) but variations in measurements could not be fully eliminated



### CPU Time Overhead
CPU Clock Time (in seconds)

<img src="results/plots/combined_ops/plot_cpu_mean_ollama-llama3.23b_100_.png" width="48%" /> <img src="results/plots/single_ops/plot_cpu_mean_ollama-llama3.23b_100_32GB-RAM-MBP-FD.png" width="48%" />

### Memory Overhead
Mean of the peak memory usage (in MB) measured over all iterations

<img src="results/plots/combined_ops/plot_mem_mean_ollama-llama3.23b_100_.png" width="48%" /> <img src="results/plots/single_ops/plot_mem_mean_ollama-llama3.23b_100_32GB-RAM-MBP-FD.png" width="48%" />