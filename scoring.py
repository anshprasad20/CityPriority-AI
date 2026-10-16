"""Explainable priority score. Five factors, each 0-100; weighted sum (weights configurable).
No UI code. Small-sample locations are shrunk toward the city average so a handful of
reports cannot dominate the ranking."""
import pandas as pd
import numpy as np
from . import config
from .safety_rules import evaluate_escalations

FACTORS = ["severity", "safety_risk", "traffic_impact", "incident_frequency", "local_context"]
WEIGHT_KEY = {"severity": "severity", "safety_risk": "safety_risk", "traffic_impact": "traffic_impact",
              "incident_frequency": "incident_frequency", "local_context": "local_context"}


def pct(s: pd.Series) -> pd.Series:
    """Percentile rank 0-100 (what share of locations this one is at or above)."""
    return s.rank(pct=True, method="average") * 100


def _shrunk_mean(total, n, city_mean, k):
    return (total + k * city_mean) / (n + k)


def compute_factors(locations, incidents, complaints, k=None) -> pd.DataFrame:
    k = config.SHRINKAGE_K if k is None else k
    loc = locations.set_index("location_id").copy()
    inc = incidents.copy()
    inc["sev_pts"] = inc["severity"].map(config.SEVERITY_POINTS)
    g = inc.groupby("location_id")
    n = g.size().reindex(loc.index, fill_value=0)

    # 1) Severity: shrunk mean severity points, percentile-ranked.
    sev_sum = g["sev_pts"].sum().reindex(loc.index, fill_value=0)
    sev = _shrunk_mean(sev_sum, n, inc["sev_pts"].mean(), k)

    # 2) Safety risk: injuries per incident (shrunk) + pedestrian + school/hospital proximity.
    inj_sum = g["injuries"].sum().reindex(loc.index, fill_value=0)
    inj = _shrunk_mean(inj_sum, n, inc["injuries"].mean(), k)
    ped = loc["pedestrian_activity"].map(config.PEDESTRIAN_SCORE).astype(float)
    prox = loc[["near_school", "near_hospital"]].max(axis=1).astype(float)
    safety = 0.5 * pct(inj) + 100 * (0.3 * ped + 0.2 * prox)

    # 3) Traffic impact (PROXY: no traffic data exists): road type + traffic-related incidents.
    traf_n = (inc[inc.incident_type.isin(config.TRAFFIC_INCIDENT_TYPES)]
              .groupby("location_id").size().reindex(loc.index, fill_value=0))
    traffic = 0.6 * loc["road_type"].map(config.ROAD_TYPE_SCORE).astype(float) + 0.4 * pct(traf_n)

    # 4) Historical frequency: incident count + open complaint backlog.
    open_c = (complaints[complaints.status.isin(config.OPEN_STATUSES)]
              .groupby("location_id").size().reindex(loc.index, fill_value=0))
    freq = 0.7 * pct(n) + 0.3 * pct(open_c)

    # 5) Local context: road condition + population density.
    ctx = (0.6 * loc["road_condition"].map(config.ROAD_CONDITION_SCORE).astype(float)
           + 0.4 * pct(loc["population_density_per_km2"]))

    out = pd.DataFrame({"severity": pct(sev), "safety_risk": safety, "traffic_impact": traffic,
                        "incident_frequency": freq, "local_context": ctx,
                        "n_incidents": n, "n_open_complaints": open_c})
    out[FACTORS] = out[FACTORS].clip(0, 100).round(2)
    return out


def score_locations(locations, incidents, complaints, weights=None) -> pd.DataFrame:
    w = weights or config.PRIORITY_WEIGHTS
    if abs(sum(w.values()) - 1.0) > 1e-6:
        raise ValueError(f"Weights must sum to 1.0 (got {sum(w.values()):.3f})")
    f = compute_factors(locations, incidents, complaints)
    for fac in FACTORS:
        f[f"pts_{fac}"] = (f[fac] * w[WEIGHT_KEY[fac]]).round(2)
    f["priority_score"] = f[[f"pts_{x}" for x in FACTORS]].sum(axis=1).round(2)
    f["top_driver"] = f[[f"pts_{x}" for x in FACTORS]].idxmax(axis=1).str.replace("pts_", "")

    esc = evaluate_escalations(locations, incidents).set_index("location_id")
    f = f.join(esc)
    f["escalated"] = f["escalated"].fillna(False)
    # Escalated locations always rank first; the score only orders within each tier.
    f["tier"] = np.where(f["escalated"], "Immediate review", "Ranked")
    f = f.sort_values(["escalated", "priority_score"], ascending=[False, False])
    f["rank"] = range(1, len(f) + 1)
    return f.reset_index()


def explain(row) -> str:
    parts = ", ".join(f"{fac.replace('_', ' ')} {row[f'pts_{fac}']:.1f}" for fac in FACTORS)
    msg = f"Priority {row['priority_score']:.1f} = {parts}. Largest driver: {row['top_driver'].replace('_', ' ')}."
    if row["escalated"]:
        msg = "IMMEDIATE REVIEW (" + "; ".join(row["reasons"]) + "). " + msg
    return msg
