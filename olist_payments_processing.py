"""
VirtuBox Data Analyst Assessment
Q3 - Data Processing Script (Olist Order Payments Dataset only)

Put olist_order_payments_dataset.csv in the same folder as this script,
or update DATA_FILE below with the full path.
"""

import pandas as pd
import numpy as np

DATA_FILE = "olist_order_payments_dataset.csv"

# ---------------------------------------------------------------
# 1. LOAD RAW DATA
# ---------------------------------------------------------------
df = pd.read_csv(DATA_FILE)
print("Raw shape:", df.shape)
print(df.head())

# ---------------------------------------------------------------
# 2. CORRECT DATA TYPES (Q3 decision #1)
# WHY: payment_installments should be a whole number (you can't pay
# in 2.5 installments) and payment_value must be numeric for any
# aggregation or comparison.
# If skipped: grouping/summing could silently misbehave if these
# ever load as text (e.g. due to a stray blank or symbol in the file).
# ---------------------------------------------------------------
df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce").astype("Int64")
df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")
df["payment_type"] = df["payment_type"].astype(str).str.strip().str.lower()

# ---------------------------------------------------------------
# 3. HANDLE MISSING VALUES (Q3 decision #2)
# WHY: a handful of rows may have missing/invalid payment_value or
# payment_installments after coercion above. These can't be
# meaningfully averaged into totals, so we isolate them rather
# than silently dropping or guessing a value.
# If skipped: sums/averages could be quietly wrong or NaN-poisoned.
# ---------------------------------------------------------------
missing_mask = df["payment_value"].isna() | df["payment_installments"].isna()
print(f"\nRows with missing payment_value/installments: {missing_mask.sum()}")
df = df[~missing_mask].copy()

# ---------------------------------------------------------------
# 4. REMOVE DUPLICATES (Q3 decision #3)
# WHY: the same order_id + payment_sequential combination should be
# unique (it's one payment installment record); an exact duplicate
# row would double-count that payment.
# If skipped: total payment value would be inflated.
# ---------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset=["order_id", "payment_sequential"])
print(f"Removed {before - len(df)} duplicate rows")

# ---------------------------------------------------------------
# 5. STANDARDIZE CATEGORICAL VALUES
# ---------------------------------------------------------------
df["payment_type"] = df["payment_type"].replace({"not_defined": "unknown"})

# ---------------------------------------------------------------
# 6. CREATE CALCULATED FIELDS
# ---------------------------------------------------------------
df["is_installment_payment"] = df["payment_installments"] > 1
df["value_per_installment"] = df["payment_value"] / df["payment_installments"].replace(0, np.nan)

# bucket installments for easier grouping
def installment_bucket(n):
    if n == 1:
        return "1 (single payment)"
    elif n <= 3:
        return "2-3"
    elif n <= 6:
        return "4-6"
    elif n <= 12:
        return "7-12"
    else:
        return "13+"

df["installment_bucket"] = df["payment_installments"].apply(installment_bucket)

# ---------------------------------------------------------------
# 7. AGGREGATION: multiple payment records per order (split payments)
# WHY: some orders have more than one payment_sequential row (e.g.
# partly voucher, partly credit card). Aggregating to order level
# lets us analyze true order value alongside payment mix.
# ---------------------------------------------------------------
order_level = (
    df.groupby("order_id")
    .agg(
        total_paid=("payment_value", "sum"),
        num_payment_parts=("payment_sequential", "count"),
        payment_types_used=("payment_type", lambda x: ", ".join(sorted(set(x)))),
        max_installments=("payment_installments", "max"),
    )
    .reset_index()
)
order_level["is_split_payment"] = order_level["num_payment_parts"] > 1

# ---------------------------------------------------------------
# 8. IDENTIFY OUTLIERS (flag, don't drop)
# WHY: dropping outliers silently would hide real (if unusual)
# high-value transactions that management would want to know about.
# ---------------------------------------------------------------
q99 = df["payment_value"].quantile(0.99)
df["is_value_outlier"] = df["payment_value"] > q99
print(f"\n99th percentile payment value: {q99:.2f}")
print(f"Outlier rows (>99th pct): {df['is_value_outlier'].sum()}")

# ---------------------------------------------------------------
# 9. PAYMENT TYPE SUMMARY (useful for Q4 insights)
# ---------------------------------------------------------------
payment_type_summary = (
    df.groupby("payment_type")
    .agg(
        transactions=("order_id", "count"),
        total_value=("payment_value", "sum"),
        avg_value=("payment_value", "mean"),
        avg_installments=("payment_installments", "mean"),
    )
    .sort_values("total_value", ascending=False)
)
print("\nPayment type summary:\n", payment_type_summary)

# ---------------------------------------------------------------
# 10. EXPORT ANALYSIS-READY FILES
# ---------------------------------------------------------------
df.to_csv("processed_payments.csv", index=False)
order_level.to_csv("order_level_payments.csv", index=False)
payment_type_summary.to_csv("payment_type_summary.csv")

print("\nSaved: processed_payments.csv, order_level_payments.csv, payment_type_summary.csv")
