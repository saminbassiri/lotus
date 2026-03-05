import gc
import json
import random
import statistics
import time
import tracemalloc
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

import pandas as pd

import lotus
from mock_lm import MockLM
from examples.provenance_examples.examples.data.sqlite_db import DB_PATH, get_data_from_sql_as_dict

from examples.provenance_examples.examples.sem_filter_sem_agg import filter_agg_movie_reviews
from examples.provenance_examples.examples.sem_join_sem_filter import join_filter_movie_reviews
from examples.provenance_examples.examples.sem_extract_sem_filter import extract_filter_movie_reviews
from examples.provenance_examples.examples.sem_topk_sem_map import topk_map_movie_reviews
from examples.provenance_examples.examples.sem_topk import topk_movie_reviews
from examples.provenance_examples.examples.sem_agg import agg_movie_reviews
from examples.provenance_examples.examples.sem_filter import filter_movie_reviews
from examples.provenance_examples.examples.sem_join import join_movie_reviews
from examples.provenance_examples.examples.sem_extract import extract_movie_reviews
from examples.provenance_examples.examples.sem_map import map_movie_reviews


RESULT_FILE = Path("provenance_benchmarks_results.jsonl")
BENCHMARKING_MODEL = "ollama/llama3.2:3b"
BENCHMARKING_SYSTEM = ""
REVIEW_TEXT_LEN = 200
RUN_ID = str(uuid.uuid4())[:8]


def benchmark_provenance_overhead(usecase_id, n_iterations=3):
    """Benchmark the time and memory overhead of provenance tracking in LOTUS."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"\n=== Starting benchmark for use case: {usecase_id} ===")
            original_df = args[0]
            current_df = original_df

            default_row_limit = 100
            row_limit = kwargs.pop("row_limit", default_row_limit)
            dataset_name = original_df.attrs.get("dataset_name", "unknown_dataset")

            if row_limit is not None:
                current_df = original_df.head(row_limit)

            actual_rows = len(current_df)
            debug = kwargs.pop("debug", True)
            raw_data = {"vanilla": [], "provenance": []}

            print(f" Recording LLM cache for {usecase_id}: {actual_rows} rows")
            cache_file = f"cache/{usecase_id}.json"
            mock_lm = MockLM(BENCHMARKING_MODEL, cache_file, mode="record")
            lotus.settings.configure(lm=mock_lm)

            func(current_df, *args[1:], **kwargs, use_prov=False)
            func(current_df, *args[1:], **kwargs, use_prov=True)

            print(
                f"\nStarting benchmark for use case: {usecase_id} with {n_iterations} iterations and {actual_rows} rows...",
                flush=True,
            )
            mock_lm.mode = "replay"
            lotus.settings.configure(lm=mock_lm)

            for i in range(n_iterations):
                modes = ["vanilla", "provenance"]
                random.shuffle(modes)

                print(f"  Iteration {i+1}/{n_iterations}... ", end="", flush=True)
                for mode in modes:
                    # set provenance flag based on mode
                    prov_flag = mode == "provenance"
                    gc.collect()
                    tracemalloc.start()

                    s_wall, s_cpu = time.perf_counter(), time.process_time()
                    func(current_df, *args[1:], **kwargs, use_prov=prov_flag)
                    e_cpu, e_wall = time.process_time(), time.perf_counter()

                    _, peak_mem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    time.sleep(3)
                    raw_data[mode].append(
                        {
                            "wall": e_wall - s_wall,
                            "cpu": e_cpu - s_cpu,
                            "mem": peak_mem / 10**6,
                        }
                    )
                print(
                    f"Iteration {i+1} done.",
                )
            time.sleep(5)

            # Calculate statistics
            stats = {}
            for idx, m in enumerate(["vanilla", "provenance"]):
                walls = [run["wall"] for run in raw_data[m]]
                cpus = [run["cpu"] for run in raw_data[m]]
                mems = [run["mem"] for run in raw_data[m]]

                stats[m] = {
                    "wall_mean": round(statistics.mean(walls), 6),
                    "wall_std": (
                        round(statistics.stdev(walls), 6) if n_iterations > 1 else 0.0
                    ),
                    "cpu_mean": round(statistics.mean(cpus), 6),
                    "cpu_std": (
                        round(statistics.stdev(cpus), 6) if n_iterations > 1 else 0.0
                    ),
                    "mem_mean": round(statistics.mean(mems), 4),
                    "mem_std": (
                        round(statistics.stdev(mems), 4) if n_iterations > 1 else 0.0
                    ),
                }

            log_entry = {
                "run_id": RUN_ID,
                "usecase_id": usecase_id,
                "timestamp": datetime.now().isoformat(),
                "function": func.__name__,
                "iterations": n_iterations,
                "results": stats,
                "metadata": {
                    "model": BENCHMARKING_MODEL,
                    "n_rows": actual_rows,
                    "dataset": dataset_name,
                    "mock_lm": True,
                    "system": BENCHMARKING_SYSTEM,
                    "text_len": REVIEW_TEXT_LEN,
                },
            }

            RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(RESULT_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            if debug:
                print_summary(func.__name__, stats, n_iterations)

            return stats

        return wrapper

    return decorator


def set_benchmark_env():
    """Configure LOTUS specific benchmarking settings."""
    # disable caching
    lotus.settings.configure(enable_cache=False)
    lm = lotus.models.LM(model=BENCHMARKING_MODEL)
    lotus.settings.configure(lm=lm)


def get_data_sql(db_path= DB_PATH, limit=1000):
    """
    Select all columns from database table.
    Set query to load data and the database path.

    Update: Reading data from VIEW that only stores 200 char long reviews

    Args:
        db_path (str): Path to the database.
        Example: "sqlite:///path/to/database.db"
    """
    return pd.DataFrame(get_data_from_sql_as_dict(db_path, limit=limit))

def get_csv_data(file_path):
    data = pd.read_csv(file_path)
    data.attrs["dataset_name"] = file_path.split("/")[-1]
    return data


def print_summary(func_name, stats, n_iterations):
    v, p = stats["vanilla"], stats["provenance"]
    print(f"\n---- Benchmark: {func_name} (Avg over {n_iterations} runs) ----")
    print(
        f"Wall Time: {v['wall_mean']:.6f}s vs {p['wall_mean']:.2f}s | OH: {(p['wall_mean'] / v['wall_mean']) - 1:+.2%}"
    )
    print(
        f"CPU Time:  {v['cpu_mean']:.6f}s vs {p['cpu_mean']:.2f}s | OH: {(p['cpu_mean'] / v['cpu_mean']) - 1:+.2%}"
    )
    print(
        f"Memory:    {v['mem_mean']:.4f}MB vs {p['mem_mean']:.2f}MB | OH: {(p['mem_mean'] / v['mem_mean']) - 1:+.2%}"
    )


# ==========================================
#   Use Case Section
# ==========================================

# ==========================================
#   Combined Use Cases
# ==========================================


@benchmark_provenance_overhead(
    usecase_id="01-UC-EXTRACT-FILTER-MAP-AGG", n_iterations=50
)
def test_extract_filter_movie_reviews(df, use_prov=False, debug=False):
    bench_df = extract_filter_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(bench_df.head())


@benchmark_provenance_overhead(
    usecase_id="02-UC-FILTER-TOPK-EXTRACT-AGG", n_iterations=50
)
def test_filter_agg_movie_reviews(df, use_prov=False, debug=False):
    bench_df = filter_agg_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(bench_df.head())


@benchmark_provenance_overhead(usecase_id="03-UC-JOIN-EXTRACT-FILTER", n_iterations=50)
def test_join_filter_movie_reviews(df, use_prov=False, debug=False):
    bench_df = join_filter_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(bench_df.head())


@benchmark_provenance_overhead(usecase_id="04-UC-TOPK-MAP-JOIN-AGG", n_iterations=50)
def test_topk_map_movie_reviews(df, use_prov=False, debug=False):
    bench_df = topk_map_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(bench_df.head())


# ==========================================
#   Single operator Use Cases
# ==========================================


@benchmark_provenance_overhead(usecase_id="05-UC-EXTRACT", n_iterations=50)
def test_extract_movie_reviews(df, use_prov=False, debug=True):
    extracted_df = extract_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(extracted_df.head())


@benchmark_provenance_overhead(usecase_id="06-UC-FILTER", n_iterations=50)
def test_filter_movie_reviews(df, use_prov=False, debug=True):
    filtered_df = filter_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(filtered_df.head())


@benchmark_provenance_overhead(usecase_id="07-UC-AGG", n_iterations=50)
def test_agg_movie_reviews(df, use_prov=False, debug=True):
    summary = agg_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(summary.head())


@benchmark_provenance_overhead(usecase_id="08-UC-JOIN", n_iterations=50)
def test_join_movie_reviews(df, use_prov=False, debug=True):
    joined = join_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(joined.head())
    return joined


@benchmark_provenance_overhead(usecase_id="09-UC-MAP", n_iterations=50)
def test_map_movie_reviews(df, use_prov=False, debug=False):
    mapped = map_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(mapped.head())


@benchmark_provenance_overhead(usecase_id="10-UC-TOPK", n_iterations=50)
def test_topk_movie_reviews(df, use_prov=False, debug=False):
    topk = topk_movie_reviews(df, use_prov=use_prov)
    if debug:
        print(topk.head())


if __name__ == "__main__":
    set_benchmark_env()
    # Set correct db path and query first to load from the correct database table
    row_limits = [10, 100, 500]
    for limit in row_limits:
        df = get_data_sql(limit=limit)
        test_extract_filter_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_filter_agg_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_join_filter_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_topk_map_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_extract_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_filter_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_agg_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_join_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_map_movie_reviews(df, debug=True, row_limit=limit)
        time.sleep(5)
        test_topk_movie_reviews(df, debug=True, row_limit=limit)
