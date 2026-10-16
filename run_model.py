"""Run the CityPriority AI model on a data folder and save the ranked results.

Usage:
    python run_model.py                                   # uses data/
    python run_model.py --data ..\03_smart_city_where_fix_first   # any folder with the 3 CSVs
    python run_model.py --out results.csv
"""
import argparse
from pathlib import Path
from core import config
from core.loader import load_data
from core.scoring import score_locations, explain

ap = argparse.ArgumentParser()
ap.add_argument("--data", default=None, help="folder containing locations.csv, incidents.csv, public_complaints.csv")
ap.add_argument("--out", default="results/ranked_locations.csv")
a = ap.parse_args()

files = None
if a.data:
    p = Path(a.data)
    files = {"locations": p / "locations.csv", "incidents": p / "incidents.csv", "complaints": p / "public_complaints.csv"}

d = load_data(files)
print(f"*** {config.DATA_LABEL} ***")
print(f"Loaded {len(d.locations):,} locations, {len(d.incidents):,} incidents, {len(d.complaints):,} complaints")
print("Validation issues:", d.issues or "none")

r = score_locations(d.locations, d.incidents, d.complaints)
r["explanation"] = r.apply(explain, axis=1)
r["reasons"] = r["reasons"].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
r.to_csv(a.out, index=False)
print(f"Scored {len(r)} locations | {int(r.escalated.sum())} need immediate review")
print(f"Saved -> {a.out}")
print(r[["rank", "location_id", "tier", "priority_score", "top_driver"]].head(10).to_string(index=False))
