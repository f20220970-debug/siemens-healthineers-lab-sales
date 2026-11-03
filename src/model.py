"""Account scoring, territory plan and pipeline comparison."""
import numpy as np
import pandas as pd
from .make_data import ASSUMPTIONS


def opportunity_value(acc):
    """Annual reagent revenue if won (INR lakh) + analyser."""
    a = ASSUMPTIONS
    reagent = acc.tests_per_day * a["working days per year"] * a["reagent revenue per test (INR)"] \
        * a["share of a won account's tests moved to the new analyser"] / 1e5
    return (reagent + a["analyser list price (INR lakh)"]).round(1)


def fit_score(acc):
    """Transparent rules a rep can explain: old analyser, immunoassay-heavy menu, relationship, vendor."""
    s = (np.clip((acc.analyser_age_yrs - 3) / 7, 0, 1) * 30
         + acc.immunoassay_share * 40
         + acc.has_relationship * 15
         + acc.current_vendor.map({"local / refurbished": 15, "Siemens (existing)": 12, "Beckman": 5,
                                   "Abbott": 2, "Roche": 0}))
    return s.round(1)


def prioritise(acc):
    a = acc.copy()
    a["value_lakh"] = opportunity_value(a)
    a["fit_score"] = fit_score(a)
    a["priority_score"] = (a.fit_score / 100 * a.value_lakh).round(1)  # expected-value style ranking
    a["tier"] = pd.qcut(a.priority_score.rank(method="first"), [0, .6, .85, 1], labels=["C", "B", "A"])
    return a.sort_values("priority_score", ascending=False)


def compare_strategies(acc, k=None, seed=3, n_sims=300):
    """Work k accounts per territory: by priority score vs by size (biggest labs) vs random; average of n_sims quarters."""
    from .make_data import simulate_pipeline
    from .make_data import ASSUMPTIONS as A
    k = k or A["rep capacity (account visits per quarter)"] // 2
    p = prioritise(acc)
    rng = np.random.default_rng(seed)
    picks = {
        "priority score": p.groupby("territory").head(k).account_id,
        "biggest labs first": p.sort_values("tests_per_day", ascending=False).groupby("territory").head(k).account_id,
        "random": p.groupby("territory").sample(k, random_state=seed).account_id,
    }
    rows = []
    for name, ids in picks.items():
        sims = [simulate_pipeline(p, ids, seed + i) for i in range(n_sims)]
        rows.append((name, len(ids),
                     round(np.mean([w.demo.sum() for w in sims]), 1), round(np.mean([w.quote.sum() for w in sims]), 1),
                     round(np.mean([w.won.sum() for w in sims]), 1),
                     round(np.mean([w.loc[w.won, "value_lakh"].sum() / 100 for w in sims]), 1)))
    return pd.DataFrame(rows, columns=["strategy", "accounts_worked", "avg_demos", "avg_quotes", "avg_wins", "avg_won_value_cr"])
