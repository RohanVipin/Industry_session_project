"""
Explains WHY the model gave a customer its score.

For XGBoost models we ask the model itself how much each input pushed the
score up or down (XGBoost's built-in "pred_contribs"). Contributions from the
one-hot columns of a category are added back together, so the answer is per
original input, such as "cons_12m", not per internal column.
"""

import numpy as np
import xgboost as xgb

CATEGORICAL = ["channel_sales", "has_gas", "origin_up"]

LABELS = {
    "channel_sales": "Sales channel",
    "origin_up": "Origin of contract",
    "has_gas": "Also a gas customer",
    "nb_prod_act": "Active products",
    "num_years_antig": "Years as customer",
    "pow_max": "Subscribed max power",
    "cons_12m": "Electricity use, last 12 months",
    "cons_gas_12m": "Gas use, last 12 months",
    "cons_last_month": "Electricity use, last month",
    "imp_cons": "Current paid consumption",
    "forecast_cons_12m": "Forecast use, next 12 months",
    "forecast_cons_year": "Forecast use, calendar year",
    "forecast_discount_energy": "Forecast energy discount",
    "forecast_meter_rent_12m": "Forecast meter rent, 12 months",
    "forecast_price_energy_off_peak": "Forecast energy price, off-peak",
    "forecast_price_energy_peak": "Forecast energy price, peak",
    "forecast_price_pow_off_peak": "Forecast power price, off-peak",
    "margin_gross_pow_ele": "Gross margin on power subscription",
    "margin_net_pow_ele": "Net margin on power subscription",
    "net_margin": "Total net margin",
    "activation_year": "Activation year",
    "activation_month": "Activation month",
    "end_year": "Contract end year",
    "renewal_year": "Renewal year",
    "tenure_days": "Contract length (days)",
    "price_off_peak_var": "Variable price, off-peak",
    "price_peak_var": "Variable price, peak",
    "price_mid_peak_var": "Variable price, mid-peak",
    "price_off_peak_fix": "Fixed price, off-peak",
    "price_peak_fix": "Fixed price, peak",
    "price_mid_peak_fix": "Fixed price, mid-peak",
}


def _original_column(feature_name: str, columns) -> str:
    # names look like "categorical__channel_sales_abc" or "numerical__cons_12m"
    name = feature_name.split("__", 1)[-1]
    for col in columns:
        if name == col or name.startswith(col + "_"):
            return col
    return name


def risk_factors(model, input_df, top_raise=3, top_lower=2):
    """Returns a list of the biggest influences on the score, or [] if the
    saved model is not an XGBoost pipeline."""

    try:
        preprocessor = model.named_steps["preprocessor"]
        classifier = model.named_steps["classifier"]
        booster = classifier.get_booster()
    except Exception:
        return []

    transformed = preprocessor.transform(input_df)
    contribs = booster.predict(xgb.DMatrix(transformed), pred_contribs=True)[0][:-1]
    names = preprocessor.get_feature_names_out()

    per_input = {}
    for name, value in zip(names, contribs):
        col = _original_column(name, input_df.columns)
        per_input[col] = per_input.get(col, 0.0) + float(value)

    total = sum(abs(v) for v in per_input.values()) or 1.0

    items = []
    for col, value in per_input.items():
        raw = input_df.iloc[0][col]
        items.append({
            "feature": col,
            "label": LABELS.get(col, col),
            "value": raw if col in CATEGORICAL else (float(raw) if not float(raw).is_integer() else int(raw)),
            "effect": "raises" if value > 0 else "lowers",
            "impact": round(abs(value) / total * 100, 1),
            "_signed": value,
        })

    raising = sorted([i for i in items if i["_signed"] > 0], key=lambda i: -i["_signed"])[:top_raise]
    lowering = sorted([i for i in items if i["_signed"] < 0], key=lambda i: i["_signed"])[:top_lower]

    result = raising + lowering
    for i in result:
        del i["_signed"]
    return result
