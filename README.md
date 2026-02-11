# Provenance Tracking for LOTUS Pipelines

## Overview
LOTUS (LLMs Over Text Unstructured and Structured Data) provides a Pandas-like API for LLM-based data processing through semantic operators. This project implements **Provenance Tracking**, which describes the origin and history of data as it is transformed through these semantic operators.

# Provenance

**Provenance** refers to the origin, history, and derivation of data.  
It explains where data comes from and how it was produced through queries, transformations, or processing steps.

**Provenance tracking** is the systematic process of capturing and maintaining provenance information as data flows through a system.  
It enables tracing outputs back to their original sources and operations, supporting transparency, debugging, and data validation.

## Use Cases of Provenance Tracking

- **Data Debugging**  
  Identify which source records or transformations caused an incorrect or unexpected result.

- **Audit & Compliance**  
  Provide traceability for regulatory requirements by showing how data was generated and modified.

- **Data Quality & Validation**  
  Verify the reliability and accuracy of outputs by tracing them back to trusted sources.

## Operator Definitions
Lotus provide following semantic operations:

| Operator      | Description |
|---------------|------------|
| sem_map       | Map each record using a natural language projection. |
| sem_filter    | Keep records that match a natural language predicate. |
| sem_extract   | Extract structured attributes from each row. |
| sem_agg       | Aggregate across records using a natural language instruction. |
| sem_topk      | Rank records by natural language criteria and return top k. |
| sem_join      | Join two datasets using a natural language matching predicate. |


# Main goal
Semantic operators extend relational algebra with natural language semantics while preserving structured outputs. We attempt to implement provenance tracking for Lotus semantic operations and provide 10 examples with benchmarks.

---

## Overview

## Main Code Components & Logic

This logic is implemented directly in the main source code for the semantic operation. (check `lotus\sem_ops\`)
The project enhances the following semantic operators with provenance capabilities:
* **sem_filter**: Returns records matching a predicate while tracking source IDs.
* **sem_join**: Joins tables based on natural language predicates.
* **sem_extract**: Extracts attributes from rows.
* **sem_map**: Maps records using natural language projections.
* **sem_topk**: Ranks and returns the best $k$ tuples.
* **sem_agg**: Aggregates data across tuples (e.g., summarization).


## Features
* **Minimal Overhead**: Provenance tracking introduces negligible CPU/Memory overhead compared to LLM inference.
* **Provenance Flag**: Users can enable tracking using `provenance=True` to see source IDs in the output.
* **Provenance Columns**: Users can specify `provenance_col` to set the column for tracking the source code.

## Testing
* **Testing the functionality**: add unit test to ensure implementation functionality (check `tests\provenance_tests.py` )
  
## Example Pipelines
The project includes 10 example pipelines (test cases) located in the repository(check `examples\provenance_examples\examples` for codes):
* **05-UC-EXTRACT**: Provenance for extraction.
* **06-UC-FILTER**: Provenance for filtering.
* **07-UC-AGG**: Provenance for aggregation.
* **08-UC-JOIN**: Provenance for joining.
* **09-UC-MAP**: Provenance for mapping.
* **10-UC-TOPK**: Provenance for top-k ranking.
* **Combined Pipelines**: 4 scripts testing combinations like `sem_extract -> sem_filter` and `sem_filter -> sem_agg`.

## Project Pipelines

The performance and the overhead of all the examples are tested via a benchmark script.(check `examples\provenance_examples\benchmark` for code and results)

---
