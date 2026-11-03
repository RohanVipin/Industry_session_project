import pandas as pd
import os


# =========================================================
# 1. LOAD DATA
# =========================================================

base_path = os.path.dirname(os.path.dirname(__file__))

client_path = os.path.join(
    base_path,
    "datasets",
    "client_data.csv"
)

price_path = os.path.join(
    base_path,
    "datasets",
    "price_data.csv"
)

client_df = pd.read_csv(client_path)
price_df = pd.read_csv(price_path)

print("Client data shape:", client_df.shape)
print("Price data shape:", price_df.shape)


# =========================================================
# 2. CONVERT DATE COLUMNS
# =========================================================

date_columns = [
    "date_activ",
    "date_end",
    "date_modif_prod",
    "date_renewal"
]

for column in date_columns:
    client_df[column] = pd.to_datetime(
        client_df[column],
        errors="coerce"
    )


price_df["price_date"] = pd.to_datetime(
    price_df["price_date"],
    errors="coerce"
)


# =========================================================
# 3. CREATE DATE FEATURES
# =========================================================

client_df["activation_year"] = (
    client_df["date_activ"].dt.year
)

client_df["activation_month"] = (
    client_df["date_activ"].dt.month
)

client_df["end_year"] = (
    client_df["date_end"].dt.year
)

client_df["renewal_year"] = (
    client_df["date_renewal"].dt.year
)


# =========================================================
# 4. CUSTOMER TENURE
# =========================================================

client_df["tenure_days"] = (
    client_df["date_end"] -
    client_df["date_activ"]
).dt.days


# =========================================================
# 5. HANDLE MISSING CATEGORICAL VALUES
# =========================================================

categorical_columns = [
    "channel_sales",
    "has_gas",
    "origin_up"
]

for column in categorical_columns:

    client_df[column] = client_df[column].fillna(
        "MISSING"
    )


# =========================================================
# 6. PRICE DATA AGGREGATION
# =========================================================

price_features = price_df.groupby("id").agg({

    "price_off_peak_var": "mean",
    "price_peak_var": "mean",
    "price_mid_peak_var": "mean",

    "price_off_peak_fix": "mean",
    "price_peak_fix": "mean",
    "price_mid_peak_fix": "mean"

}).reset_index()


print(
    "\nAggregated price data shape:",
    price_features.shape
)


# =========================================================
# 7. MERGE CLIENT + PRICE DATA
# =========================================================

final_df = client_df.merge(
    price_features,
    on="id",
    how="left"
)


print(
    "\nFinal dataset shape:",
    final_df.shape
)


# =========================================================
# 8. DROP ORIGINAL DATE COLUMNS
# =========================================================

final_df = final_df.drop(
    columns=date_columns
)


# =========================================================
# 9. DROP CUSTOMER ID
# =========================================================

final_df = final_df.drop(
    columns=["id"]
)


# =========================================================
# 10. SAVE PROCESSED DATA
# =========================================================

output_path = os.path.join(
    base_path,
    "datasets",
    "processed_data.csv"
)

final_df.to_csv(
    output_path,
    index=False
)


print(
    "\nProcessed dataset saved to:"
)

print(output_path)


# =========================================================
# 11. FINAL INFORMATION
# =========================================================

print(
    "\nFinal columns:"
)

print(final_df.columns.tolist())

print(
    "\nMissing values:"
)

print(
    final_df.isnull().sum()
)

print(
    "\n========== PREPROCESSING COMPLETED =========="
)