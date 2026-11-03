import pandas as pd
from src.model import opportunity_value, fit_score


def acc(**kw):
    base = dict(account_id="A", territory="Bengaluru", type="hospital", tests_per_day=1000, immunoassay_share=0.5,
                current_vendor="Roche", analyser_age_yrs=10, has_relationship=True, budget_month=1)
    base.update(kw); return pd.DataFrame([base])


def test_value_by_hand():
    # 1000 tests x 330 days x INR 55 x 0.6 = INR 108.9 lakh reagent + 60 lakh analyser
    assert opportunity_value(acc()).iloc[0] == 168.9


def test_fit_by_hand():
    # age 10 -> 30, immunoassay 0.5 -> 20, relationship 15, Roche 0
    assert fit_score(acc()).iloc[0] == 65.0
    assert fit_score(acc(current_vendor="local / refurbished", has_relationship=False, analyser_age_yrs=3)).iloc[0] == 35.0
