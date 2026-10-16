"""Stage 2 check: score all locations on the real data and show the top of the ranking."""
import pandas as pd
from core import config
from core.loader import load_data
from core.scoring import score_locations, explain

d = load_data()
r = score_locations(d.locations, d.incidents, d.complaints)
print(f"\n*** {config.DATA_LABEL} ***")
print(f"\nLocations scored: {len(r)} | escalated: {int(r.escalated.sum())}")
cols = ["rank", "location_id", "tier", "priority_score", "n_incidents", "top_driver"]
pd.set_option("display.width", 140)
print("\nTop 10:\n", r[cols].head(10).to_string(index=False))
print("\nHighest-scoring NON-escalated:\n", r[~r.escalated][cols].head(5).to_string(index=False))
print("\nExample explanation:\n", explain(r.iloc[0]))
print("\nScore spread:", r.priority_score.describe().round(1).to_dict())
