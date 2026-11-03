"""Simulated lab and hospital accounts in two sales territories (Delhi NCR / Gurugram and Bengaluru).

Not Siemens Healthineers data. Every assumption is listed in ASSUMPTIONS and in the README.
"""
import numpy as np
import pandas as pd

SEED = 3
ASSUMPTIONS = {
    "reagent revenue per test (INR)": 55,
    "working days per year": 330,
    "analyser list price (INR lakh)": 60,
    "share of a won account's tests moved to the new analyser": 0.6,
    "rep capacity (account visits per quarter)": 120,
}
TYPES = {"hospital": .40, "lab chain branch": .30, "standalone lab": .20, "diagnostic centre": .10}
COMPETITORS = {"Roche": .30, "Abbott": .25, "Beckman": .15, "Siemens (existing)": .10, "local / refurbished": .20}


def simulate(n=600, seed=SEED):
    rng = np.random.default_rng(seed)
    t = rng.choice(list(TYPES), n, p=list(TYPES.values()))
    tests = np.where(t == "hospital", rng.lognormal(6.6, .55, n),
             np.where(t == "lab chain branch", rng.lognormal(6.3, .5, n),
             np.where(t == "standalone lab", rng.lognormal(5.6, .5, n), rng.lognormal(5.9, .5, n))))
    acc = pd.DataFrame({
        "account_id": [f"A{i:04d}" for i in range(n)],
        "territory": rng.choice(["Delhi NCR", "Bengaluru"], n, p=[.55, .45]),
        "type": t,
        "tests_per_day": tests.round(0).astype(int),
        "immunoassay_share": rng.beta(3, 5, n).round(2),
        "current_vendor": rng.choice(list(COMPETITORS), n, p=list(COMPETITORS.values())),
        "analyser_age_yrs": rng.integers(1, 12, n),
        "has_relationship": rng.random(n) < 0.3,
        "budget_month": rng.integers(1, 13, n),
    })
    # true (hidden) win probability for the pipeline simulation
    z = (-1.6 + 0.18 * (acc.analyser_age_yrs - 6) + 1.2 * acc.has_relationship
         + 1.0 * (acc.current_vendor == "local / refurbished") + 0.9 * (acc.current_vendor == "Siemens (existing)")
         + 1.5 * (acc.immunoassay_share - 0.37) + 0.3 * (acc["type"] == "lab chain branch"))
    acc["true_win_p"] = 1 / (1 + np.exp(-z))
    return acc


def simulate_pipeline(acc, worked_ids, seed=SEED):
    """Accounts the rep works go through demo -> quote -> won; returns outcomes."""
    rng = np.random.default_rng(seed + 1)
    w = acc[acc.account_id.isin(worked_ids)].copy()
    w["demo"] = rng.random(len(w)) < 0.55 + 0.25 * w.has_relationship
    w["quote"] = w.demo & (rng.random(len(w)) < 0.6)
    w["won"] = w.quote & (rng.random(len(w)) < w.true_win_p.clip(0.05, 0.9))
    return w
