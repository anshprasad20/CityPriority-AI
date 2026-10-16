"""Hard safety-escalation rules. They never use the weighted score, so the score
can never suppress an urgent concern. 'Unresolved' means resolved == 0 (see the
data-quality report: that field is itself imperfect, so flagged sites need inspection)."""
import pandas as pd
from . import config

RULES = {
    "R1": "Unresolved Critical incident with injury",
    "R2": "Unresolved High/Critical injury incident near a school/hospital with high pedestrian activity",
    "R3": "Unresolved incidents at this location total {n}+ injuries",
}


def evaluate_escalations(locations: pd.DataFrame, incidents: pd.DataFrame) -> pd.DataFrame:
    """Return one row per location: escalated (bool) and reasons (list of text)."""
    cfg = config.ESCALATION
    reasons = {lid: [] for lid in locations["location_id"]}
    u = incidents[incidents["resolved"] == 0].merge(locations, on="location_id", how="left")

    r1 = u[(u.severity == "Critical") & (u.injuries >= cfg["critical_with_injury_min_injuries"])]
    for lid in r1.location_id.unique():
        reasons[lid].append(RULES["R1"])

    sensitive = (u.near_school == 1) | (u.near_hospital == 1)
    r2 = u[u.severity.isin(["High", "Critical"]) & sensitive & (u.pedestrian_activity == "High")
           & (u.injuries >= cfg["sensitive_site_min_injuries"])]
    for lid in r2.location_id.unique():
        reasons[lid].append(RULES["R2"])

    inj = u.groupby("location_id").injuries.sum()
    for lid in inj[inj >= cfg["unresolved_injuries_total"]].index:
        reasons[lid].append(RULES["R3"].format(n=cfg["unresolved_injuries_total"]))

    out = pd.DataFrame({"location_id": list(reasons), "reasons": list(reasons.values())})
    out["escalated"] = out["reasons"].str.len() > 0
    return out
