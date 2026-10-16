"""Export Stage 2 results (+ simple evidence-confidence) as JSON for the dashboard."""
import json, pandas as pd, numpy as np
from pathlib import Path
from core.loader import load_data
from core.scoring import score_locations
from core.quality import run_quality_checks
d = load_data(); L, I, C = d.locations, d.incidents, d.complaints
r = score_locations(L, I, C).merge(L, on="location_id")
end = I.timestamp.max()
g = I.groupby("location_id")
last = g.timestamp.max().reindex(r.location_id)
contra = I[(I.resolved == 0) & I.resolution_hours.notna()].groupby("location_id").size().reindex(r.location_id, fill_value=0)
lowsev = I[(I.injuries >= 2) & (I.severity == "Low")].groupby("location_id").size().reindex(r.location_id, fill_value=0)
types = I.pivot_table(index="location_id", columns="incident_type", values="incident_id", aggfunc="count", fill_value=0).reindex(r.location_id, fill_value=0)
rows = []
for i, x in enumerate(r.itertuples()):
    n = x.n_incidents; cs = contra.iloc[i]
    vol = min(n / 12, 1); cshare = cs / n if n else 1; days = (end - last.iloc[i]).days if pd.notna(last.iloc[i]) else 999
    conf = round(100 * (0.5 * vol + 0.3 * (1 - cshare) + 0.2 * (1 if days <= 90 else 0)))
    gaps = []
    if n < 5: gaps.append(["Few incident records (%d)" % n, "Collect more reports or inspect on site"])
    if cs: gaps.append(["%d unresolved incident(s) also list a resolution time" % cs, "Confirm status with the data owner"])
    if lowsev.iloc[i]: gaps.append(["Injuries recorded but severity is Low", "Verify severity by field inspection"])
    if days > 90: gaps.append(["No incident in the last 90 days (%d days)" % days, "Check whether the issue is still active"])
    gaps += [["Repair cost not in dataset", "Estimate cost after inspection"], ["Traffic counts not in dataset (road type used as proxy)", "Obtain traffic data"]]
    rows.append(dict(id=x.location_id, z=x.zone, lat=round(x.latitude, 5), lon=round(x.longitude, 5), rt=x.road_type, rc=x.road_condition,
        pa=x.pedestrian_activity, sc=int(x.near_school), ho=int(x.near_hospital), s=float(x.priority_score), rk=int(x.rank), esc=bool(x.escalated), unc=bool(x.escalated and cs > 0),
        why=list(x.reasons), f=[float(getattr(x, k)) for k in ["severity", "safety_risk", "traffic_impact", "incident_frequency", "local_context"]],
        p=[float(getattr(x, "pts_" + k)) for k in ["severity", "safety_risk", "traffic_impact", "incident_frequency", "local_context"]],
        n=int(n), oc=int(x.n_open_complaints), cf=int(conf), gaps=gaps, ty=[int(v) for v in types.iloc[i].values]))
m = I.groupby(I.timestamp.dt.month).size().tolist()
out = dict(rows=rows, types=list(types.columns), month=m, nI=len(I), nC=len(C), nL=len(L),
    q=[dict(c=f.check, k=f.count, t=f.total, lv=f.level) for f in run_quality_checks(d)[:5] if f.total > 1])
dest = Path(__file__).resolve().parent / "dashboard"
dest.mkdir(exist_ok=True)
json.dump(out, open(dest / "dash_data.json", "w"), separators=(",", ":"))
print(len(rows), "rows;", round(len(json.dumps(out)) / 1024), "KB; low-conf:", sum(1 for x in rows if x["cf"] < 40))
