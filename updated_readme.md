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

- **Reproducibility**  
  Recreate results by understanding the exact transformations and inputs used.

- **Trust & Transparency**  
  Help users assess the credibility of data by exposing its origins and processing history.

- **Impact Analysis**  
  Determine which outputs are affected when a source dataset changes.



# Semantic Operators
LLM-Powered Relational Primitives with Provenance

Semantic operators extend relational algebra with natural language semantics while preserving structured outputs and explicit provenance tracking.

They allow users to express data transformations declaratively using natural language — without sacrificing auditability or composability.

---

## Overview

Traditional relational operators require symbolic predicates:

SELECT * FROM reviews WHERE rating > 4;

Semantic operators allow intent-driven execution:

sem_filter(reviews, "Mentions battery problems")

Each operator:

- Is declarative
- Produces structured tabular output
- Attaches explicit provenance metadata
- Is composable with other operators
- Is model-agnostic

---

## Operator Definitions

| Operator      | Description |
|---------------|------------|
| sem_map       | Map each record using a natural language projection. |
| sem_filter    | Keep records that match a natural language predicate. |
| sem_extract   | Extract structured attributes from each row. |
| sem_agg       | Aggregate across records using a natural language instruction. |
| sem_topk      | Rank records by natural language criteria and return top k. |
| sem_join      | Join two datasets using a natural language matching predicate. |

---

## Provenance Model

All semantic operators attach lineage metadata to support traceability and reproducibility.

| Field | Meaning |
|-------|---------|
| prov.source_row | Originating input row |
| prov.source_rows | Set of contributing rows |
| prov.source_pair | Pair of input rows (join) |
| prov.score_explanation | Ranking explanation |
| prov.match_rationale | Join reasoning |
| prov.op | Operator name |
| prov.prompt | Natural language instruction |
| prov.model | Model used |

Example provenance object:

{
  "op": "sem_filter",
  "prompt": "Mentions battery problems",
  "model": "gpt-4o",
  "input_ids": ["r2"],
  "timestamp": "2026-02-10T12:01:33Z"
}

---

# Operator Examples

---

## 1. sem_map

Definition: Maps each record using a natural language projection.

Usage:

sem_map(
    reviews,
    "Create a one-sentence summary and sentiment."
)

Input:

| row_id | review_text |
|--------|------------|
| r1 | Battery lasts forever. Camera is decent. |
| r2 | Great photos, but battery dies fast. |
| r3 | Solid phone overall. |

Output:

| out_id | summary | sentiment | prov.source_row |
|--------|---------|-----------|-----------------|
| m1 | Long-lasting battery and acceptable camera. | positive | r1 |
| m2 | Excellent camera but poor battery life. | mixed | r2 |
| m3 | Generally a good all-around phone. | neutral | r3 |

---

## 2. sem_filter

Definition: Filters rows based on a natural language predicate.

Usage:

sem_filter(
    reviews,
    "Mentions battery problems"
)

Output:

| row_id | review_text | prov.source_row |
|--------|------------|-----------------|
| f1 | Great photos, but battery dies fast. | r2 |

---

## 3. sem_extract

Definition: Extracts structured attributes from each record using NL instructions.

Usage:

sem_extract(
    tickets,
    "Extract issue_type, urgency, and identifiers."
)

Input:

| row_id | ticket_text |
|--------|------------|
| t1 | Order #A102 arrived damaged. Need replacement ASAP. |
| t2 | Can’t log in since yesterday. |
| t3 | Cancel subscription next month. |

Output:

| out_id | issue_type | urgency | identifiers | prov.source_row |
|--------|-----------|---------|-------------|-----------------|
| e1 | damaged_delivery | high | Order #A102 | t1 |
| e2 | login_issue | high | – | t2 |
| e3 | subscription_cancellation | medium | – | t3 |

---

## 4. sem_agg

Definition: Aggregates across records using a natural language aggregation instruction.

Usage:

sem_agg(
    meeting_notes,
    "Summarize decisions, risks, and action items."
)

Input:

| row_id | note |
|--------|------|
| n1 | Team agreed to ship MVP by March 1. |
| n2 | Biggest risk: data pipeline instability. |
| n3 | Action: Priya will draft rollout plan. |

Output:

| out_id | decisions | risks | action_items | prov.source_rows |
|--------|----------|-------|--------------|------------------|
| a1 | Ship MVP by March 1 | Pipeline instability | Priya drafts rollout plan | [n1, n2, n3] |

---

## 5. sem_topk

Definition: Ranks records according to natural language sorting criteria and returns top k.

Usage:

sem_topk(
    candidates,
    "Best fit for senior backend role with strong cloud experience",
    k=2
)

Input:

| row_id | profile |
|--------|--------|
| c1 | 3 years backend, strong Python, some AWS |
| c2 | 8 years backend, led teams, deep AWS + Kubernetes |
| c3 | 2 years full-stack, React focus |
| c4 | 6 years data engineering, Spark, AWS |

Output:

| rank | row_id | prov.source_row | prov.score_explanation |
|------|--------|-----------------|------------------------|
| 1 | c2 | c2 | Strong seniority + deep cloud leadership |
| 2 | c4 | c4 | Strong AWS systems experience |

---

## 6. sem_join

Definition: Joins two datasets using a natural language matching predicate.

Usage:

sem_join(
    customers,
    emails,
    "Email likely belongs to the customer based on name/context"
)

Customers:

| row_id | customer_name | note |
|--------|--------------|------|
| u1 | Alex Chen | Uses ACME CRM; complained about billing |
| u2 | Maria Garcia | Asked about refunds |

Emails:

| row_id | from | subject |
|--------|------|---------|
| e10 | alex.chen@corp.com | Billing issue with ACME |
| e11 | m.garcia@gmail.com | Refund request |
| e12 | someone@else.com | Hello |

Output:

| out_id | customer_row | email_row | prov.source_pair | prov.match_rationale |
|--------|-------------|-----------|------------------|----------------------|
| j1 | u1 | e10 | (u1, e10) | Name + billing context match |
| j2 | u2 | e11 | (u2, e11) | Name + refund context match |

---
   ↓

