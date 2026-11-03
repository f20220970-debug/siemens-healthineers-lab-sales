import re
from pathlib import Path
import duckdb
from src.make_data import simulate, ASSUMPTIONS
from src.model import prioritise, compare_strategies

OUT = Path("output"); OUT.mkdir(exist_ok=True)
acc = simulate()
p = prioritise(acc)
p.drop(columns="true_win_p").to_csv(OUT / "account_priority_list.csv", index=False)
con = duckdb.connect(); con.register("scored", p.assign(tier=p.tier.astype(str)))
parts = re.split(r"^-- name: (\w+)\s*$", Path("sql/segments.sql").read_text(), flags=re.M)
for i in range(1, len(parts), 2):
    df = con.execute(parts[i + 1].strip().rstrip(";")).df(); df.to_csv(OUT / f"{parts[i]}.csv", index=False)
    print(f"\n== {parts[i]}\n{df.to_string(index=False)}")
print("\n== assumptions", ASSUMPTIONS)
print(f"\naccounts={len(p)} total value INR {p.value_lakh.sum()/100:.0f} Cr; tier A={int((p.tier=='A').sum())} holding {p[p.tier=='A'].value_lakh.sum()/p.value_lakh.sum():.0%} of value")
cs = compare_strategies(acc); cs.to_csv(OUT / "strategy_comparison.csv", index=False)
print("\n== strategy comparison (60 accounts per territory, average of 300 simulated quarters)\n", cs.to_string(index=False))
print("\n== top 10\n", p.head(10)[["account_id", "territory", "type", "tests_per_day", "current_vendor", "analyser_age_yrs", "value_lakh", "fit_score", "priority_score"]].to_string(index=False))
