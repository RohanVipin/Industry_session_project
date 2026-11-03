"""
Retention recommendation engine.

Plain, readable business rules that turn a churn risk score plus a few
facts from the customer's own record into a suggested next step. There is no
machine learning in this file: every rule and every threshold is written out
below so it can be read, questioned and changed by anyone.

Every fact the rules use comes from the 33 customer fields already in the
dataset. Nothing has to be typed in separately.

All thresholds are constants at the top. Change them here and the API and the
web page both pick the new values up automatically.
"""

# ---------------------------------------------------------------------------
# THRESHOLDS  (edit these to change the behaviour)
# ---------------------------------------------------------------------------

# Risk bands, applied to the model's churn score (0 to 1).
# Checked on held-out data: customers scoring >= 0.50 churned about 22% of
# the time, versus 9.7% on average.
HIGH_RISK_THRESHOLD = 0.50
MEDIUM_RISK_THRESHOLD = 0.35

# "High revenue" = net_margin at or above the 75th percentile of the
# training data (243.1). net_margin is the dataset's closest revenue measure.
HIGH_REVENUE_NET_MARGIN = 243.1

# "Paying above forecast price" = the customer's average off-peak variable
# price (price_off_peak_var) is at least 5% above the forecast off-peak energy
# price (forecast_price_energy_off_peak). This is the dataset's closest thing
# to a billing concern: the customer is being charged more than was forecast.
PRICE_ABOVE_FORECAST_RATIO = 1.05

# "Newer customer" = 3 years or less as a customer (num_years_antig).
# In the training data these customers left about 14% of the time versus
# about 10% overall.
NEWER_CUSTOMER_MAX_YEARS = 3

# "Declining engagement" = electricity use last month was less than half of
# the customer's usual monthly use (cons_12m / 12).
DECLINING_USAGE_RATIO = 0.5


# ---------------------------------------------------------------------------
# RISK LEVEL
# ---------------------------------------------------------------------------

def risk_level(probability: float) -> str:
    if probability >= HIGH_RISK_THRESHOLD:
        return "High"
    if probability >= MEDIUM_RISK_THRESHOLD:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# SIGNALS  (facts about the customer that the rules look at)
# ---------------------------------------------------------------------------

def get_signals(data: dict) -> dict:
    """Each signal is {label, met, detail}."""

    # High revenue
    net_margin = data["net_margin"]

    # Paying above forecast price
    actual_price = data["price_off_peak_var"]
    forecast_price = data["forecast_price_energy_off_peak"]
    if forecast_price > 0:
        price_ratio = actual_price / forecast_price
        above_forecast = price_ratio >= PRICE_ABOVE_FORECAST_RATIO
        price_detail = (
            f"Average off-peak price is {price_ratio - 1:+.1%} versus the forecast price "
            f"(flagged at +{PRICE_ABOVE_FORECAST_RATIO - 1:.0%} or more)"
        )
    else:
        above_forecast = False
        price_detail = "No forecast price available, so the comparison can't be made"

    # Newer customer
    years = data["num_years_antig"]

    # Declining engagement
    monthly_average = data["cons_12m"] / 12
    if monthly_average > 0:
        usage_ratio = data["cons_last_month"] / monthly_average
        declining = usage_ratio < DECLINING_USAGE_RATIO
        usage_detail = (
            f"Last month's use was {usage_ratio:.0%} of the usual monthly average "
            f"(flagged below {DECLINING_USAGE_RATIO:.0%})"
        )
    else:
        declining = False
        usage_detail = "No electricity use in the last 12 months, so a trend can't be judged"

    return {
        "high_revenue": {
            "label": "High revenue",
            "met": net_margin >= HIGH_REVENUE_NET_MARGIN,
            "detail": f"Net margin is {net_margin:,.2f} (flagged at {HIGH_REVENUE_NET_MARGIN:,.1f} or more)",
        },
        "price_above_forecast": {
            "label": "Paying above forecast price",
            "met": above_forecast,
            "detail": price_detail,
        },
        "newer_customer": {
            "label": "Newer customer",
            "met": years <= NEWER_CUSTOMER_MAX_YEARS,
            "detail": f"{years:g} years as a customer (flagged at {NEWER_CUSTOMER_MAX_YEARS} or fewer)",
        },
        "declining_engagement": {
            "label": "Declining engagement",
            "met": declining,
            "detail": usage_detail,
        },
    }


# ---------------------------------------------------------------------------
# RULES  (checked top to bottom; the first match is the main suggestion)
# ---------------------------------------------------------------------------

RULES = [
    {
        "id": "high_revenue",
        "situation": "High risk + high revenue",
        "action": "Prioritize for human review",
        "levels": ["High"],
        "signal": "high_revenue",
        "explanation": (
            "This customer is likely to leave and brings in a lot of revenue, so losing them "
            "would be costly. A person should look at the account and decide how to reach out."
        ),
    },
    {
        "id": "pricing",
        "situation": "High risk + paying above forecast price",
        "action": "Investigate billing and pricing",
        "levels": ["High"],
        "signal": "price_above_forecast",
        "explanation": (
            "This customer is likely to leave and is being charged more than the forecast "
            "price. Checking that their bills and rates are correct and fair removes a "
            "possible reason for leaving."
        ),
    },
    {
        "id": "contract",
        "situation": "High risk + newer customer",
        "action": "Consider an appropriate contract offer",
        "levels": ["High"],
        "signal": "newer_customer",
        "explanation": (
            "This customer is likely to leave and has been with the company only a few years. "
            "Newer customers have left more often in the past data. A longer-term or loyalty "
            "offer that suits them may help build commitment."
        ),
    },
    {
        "id": "engagement",
        "situation": "Medium risk + declining engagement",
        "action": "Send a re-engagement campaign",
        "levels": ["Medium"],
        "signal": "declining_engagement",
        "explanation": (
            "The risk is moderate and the customer is using noticeably less than usual. A "
            "friendly re-engagement message may help before the risk grows."
        ),
    },
]

FALLBACK = {
    "id": "none",
    "situation": "No rule matched",
    "action": "No special action. Keep monitoring.",
    "explanation": (
        "None of the four retention rules apply to this combination of risk level and "
        "customer facts, so standard account handling is enough."
    ),
}


def recommend(probability: float, data: dict) -> dict:
    level = risk_level(probability)
    signals = get_signals(data)

    matched = [
        r for r in RULES
        if level in r["levels"] and signals[r["signal"]]["met"]
    ]

    main = matched[0] if matched else FALLBACK

    explanation = main["explanation"]
    if len(matched) > 1:
        explanation += " Other rules also apply, listed below."

    return {
        "risk_level": level,
        "action": main["action"],
        "rule": main["situation"],
        "explanation": explanation,
        "also_applies": [
            {"rule": r["situation"], "action": r["action"]} for r in matched[1:]
        ],
        "signals": [
            {"key": k, **v} for k, v in signals.items()
        ],
    }


def describe_rules() -> dict:
    """What the web page shows in its 'How the rules work' section."""
    return {
        "thresholds": {
            "high_risk_at_or_above": HIGH_RISK_THRESHOLD,
            "medium_risk_at_or_above": MEDIUM_RISK_THRESHOLD,
            "high_revenue_net_margin": HIGH_REVENUE_NET_MARGIN,
            "price_above_forecast_ratio": PRICE_ABOVE_FORECAST_RATIO,
            "newer_customer_max_years": NEWER_CUSTOMER_MAX_YEARS,
            "declining_usage_ratio": DECLINING_USAGE_RATIO,
        },
        "rules": [
            {"situation": r["situation"], "action": r["action"]} for r in RULES
        ],
    }
