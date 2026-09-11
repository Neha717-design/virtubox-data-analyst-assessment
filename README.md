# Data Analyst Assessment — README / Methodology

**Candidate:** Neha
**Assessment:** VirtuBox Infotech — Data Analyst Assessment Test
**Domain:** Retail / E-Commerce

## Project Overview

This project analyzes customer payment behavior on the Olist Brazilian e-commerce marketplace to identify business opportunities around checkout design, installment strategy, and payment-related risk.

**Business problem:** How do customers pay on the Olist marketplace, and does payment behavior — method choice, installment plans — relate to transaction value in ways that could inform pricing or checkout strategy?

## Dataset

- **Name:** Olist Order Payments Dataset
- **Source:** Kaggle — Brazilian E-Commerce Public Dataset by Olist (kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Size:** 103,886 rows × 5 columns, covering 99,441 unique orders
- **Scope decision:** This analysis uses the payments file independently rather than joining it with the other Olist tables (orders, customers, products, reviews). The file exceeds the 50,000-row threshold on its own, which kept the analysis focused and manageable within the assessment's time limit. This tradeoff is discussed further in the Limitations section.

## Methodology

**Tools:** Python, Pandas

**Process:**
1. **Type correction** — converted `payment_installments` to integer and `payment_value` to numeric; standardized `payment_type` text
2. **Missing value check** — verified completeness of key fields (0 missing values found)
3. **Duplicate check** — verified uniqueness on `order_id` + `payment_sequential` (0 duplicates found)
4. **Standardization** — normalized non-standard category labels (e.g. `not_defined` → `unknown`)
5. **Calculated fields** — derived `is_installment_payment`, `value_per_installment`, and `installment_bucket`
6. **Aggregation** — built payment-type summary and order-level (multi-payment) summary tables
7. **Outlier flagging** — flagged transactions above the 99th percentile of payment value, retained rather than removed

## Key Deliverables

| File | Description |
|---|---|
| `olist_payments_processing.py` | Python script — cleaning, processing, and feature engineering |
| `processed_payments.csv` | Cleaned, transaction-level dataset with calculated fields |
| `order_level_payments.csv` | Order-level aggregation (handles split payments) |
| `payment_type_summary.csv` | Summary statistics by payment type |
| `dashboard_kpis.csv` | Executive KPI figures for the dashboard |
| Dashboard (Looker Studio / screenshots) | Executive dashboard with KPIs, segment analysis, trend, and filters |
| `olist_payments_presentation.pptx` | 7-slide management presentation |
| Google Sheet | All worksheets (Data, Q1–Q10) |

## Summary of Findings

- Credit card accounts for 74% of transactions and 78% of total payment value
- Installment payments are used exclusively with credit card (avg 3.5 installments); all other payment types are single-payment only
- Average transaction value rises with installment count, from R$112 (1 installment) to R$414 (13+)
- 1,039 transactions (1%) are value outliers, averaging R$1,652 vs. R$139 typical
- Split-payment orders are rare (3%) and show minimal value difference from single-payment orders

## Recommendations

1. Promote installment options at credit card checkout
2. Investigate and classify high-value outlier transactions
3. Deprioritize split-payment checkout features

## Limitations

- Single-table scope means no link to product, customer, delivery, or satisfaction data
- No date/timestamp field — findings represent a snapshot, not a time-based trend
- Payment method usage reflects platform capability as well as customer choice; the two cannot be fully separated with this dataset

## AI Tool Usage

AI (Claude, Anthropic) was used for dataset selection, writing and debugging the processing script, computing summary statistics, and structuring the analysis and presentation. See Q10 in the Google Sheet for full details.
