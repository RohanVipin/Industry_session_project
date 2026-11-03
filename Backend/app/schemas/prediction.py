from pydantic import BaseModel


class PredictionInput(BaseModel):
    channel_sales: str

    cons_12m: float
    cons_gas_12m: float
    cons_last_month: float

    forecast_cons_12m: float
    forecast_cons_year: float
    forecast_discount_energy: float
    forecast_meter_rent_12m: float

    forecast_price_energy_off_peak: float
    forecast_price_energy_peak: float
    forecast_price_pow_off_peak: float

    has_gas: str

    imp_cons: float
    margin_gross_pow_ele: float
    margin_net_pow_ele: float

    nb_prod_act: float
    net_margin: float
    num_years_antig: float

    origin_up: str
    pow_max: float

    activation_year: float
    activation_month: float
    end_year: float
    renewal_year: float
    tenure_days: float

    price_off_peak_var: float
    price_peak_var: float
    price_mid_peak_var: float

    price_off_peak_fix: float
    price_peak_fix: float
    price_mid_peak_fix: float