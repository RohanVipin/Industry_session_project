import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns


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


# =========================================================
# 2. BASIC INFORMATION
# =========================================================

print("\n========== CLIENT DATA ==========")

print("Shape:", client_df.shape)

print("\nChurn Distribution:")
print(client_df["churn"].value_counts())

print("\nChurn Percentage:")
print(
    client_df["churn"].value_counts(normalize=True) * 100
)


# =========================================================
# 3. NUMERICAL FEATURES
# =========================================================

numeric_columns = client_df.select_dtypes(
    include=["int64", "float64"]
).columns

print("\n========== NUMERICAL FEATURES ==========")

print(numeric_columns.tolist())


# =========================================================
# 4. CATEGORICAL FEATURES
# =========================================================

categorical_columns = client_df.select_dtypes(
    include=["object"]
).columns

print("\n========== CATEGORICAL FEATURES ==========")

print(categorical_columns.tolist())


# =========================================================
# 5. SUMMARY STATISTICS
# =========================================================

print("\n========== SUMMARY STATISTICS ==========")

print(
    client_df[numeric_columns].describe()
)


# =========================================================
# 6. CHURN VISUALIZATION
# =========================================================

plt.figure(figsize=(6, 4))

sns.countplot(
    x="churn",
    data=client_df
)

plt.title("Customer Churn Distribution")
plt.xlabel("Churn")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    os.path.join(
        base_path,
        "churn_distribution.png"
    )
)

plt.show()


# =========================================================
# 7. CHURN VS NUMERICAL FEATURES
# =========================================================

important_features = [
    "cons_12m",
    "cons_last_month",
    "forecast_cons_12m",
    "forecast_cons_year",
    "forecast_discount_energy",
    "imp_cons",
    "margin_net_pow_ele",
    "net_margin",
    "num_years_antig",
    "pow_max"
]

for feature in important_features:

    plt.figure(figsize=(7, 4))

    sns.boxplot(
        x="churn",
        y=feature,
        data=client_df
    )

    plt.title(f"{feature} vs Churn")
    plt.xlabel("Churn")
    plt.ylabel(feature)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            base_path,
            f"{feature}_vs_churn.png"
        )
    )

    plt.show()


# =========================================================
# 8. CORRELATION WITH CHURN
# =========================================================

correlation = (
    client_df[numeric_columns]
    .corr()["churn"]
    .sort_values(ascending=False)
)

print("\n========== CORRELATION WITH CHURN ==========")

print(correlation)


# =========================================================
# 9. PRICE DATA INFORMATION
# =========================================================

print("\n========== PRICE DATA ==========")

print("Shape:", price_df.shape)

print("\nPrice Data Columns:")
print(price_df.columns.tolist())

print("\nPrice Data Summary:")
print(
    price_df.describe()
)

print("\n========== CATEGORICAL VALUES ==========")

for column in ["channel_sales", "has_gas", "origin_up"]:
    print(f"\n{column}:")
    print(client_df[column].value_counts())
print("\n========== EDA COMPLETED ==========")