import pandas as pd, pytest
from core import config
from core.scoring import score_locations, compute_factors, FACTORS
from core.safety_rules import evaluate_escalations


def mk():
    loc = pd.DataFrame({"location_id": ["A", "B", "C"], "zone": "Z", "road_type": ["Highway", "Local", "Local"],
        "road_condition": ["Poor", "Good", "Good"], "population_density_per_km2": [20000, 5000, 5000],
        "near_school": [1, 0, 0], "near_hospital": [0, 0, 0], "pedestrian_activity": ["High", "Low", "Low"],
        "latitude": 16.5, "longitude": 80.5})
    rows = []
    for i in range(6):   # A: many High incidents, unresolved, injuries
        rows.append(("IA%d" % i, "A", "2025-01-01", "Collision", "High", 1, "Citizen", 0, 5.0))
    for i in range(3):
        rows.append(("IB%d" % i, "B", "2025-01-01", "Pothole", "Low", 0, "Citizen", 1, 5.0))
    rows.append(("IC0", "C", "2025-01-01", "Pothole", "Critical", 1, "Citizen", 0, 5.0))  # lone, tiny sample
    inc = pd.DataFrame(rows, columns=config.REQUIRED_COLUMNS["incidents"])
    inc["timestamp"] = pd.to_datetime(inc["timestamp"])
    com = pd.DataFrame({"complaint_id": ["C1"], "location_id": ["A"], "created_at": pd.to_datetime(["2025-02-01"]),
        "category": ["Traffic"], "priority_reported": ["High"], "status": ["Open"], "days_to_resolution": [None]})
    return loc, inc, com


def test_weights_sum_to_one():
    assert sum(config.PRIORITY_WEIGHTS.values()) == pytest.approx(1.0)


def test_factors_within_0_100():
    f = compute_factors(*mk())
    assert f[FACTORS].min().min() >= 0 and f[FACTORS].max().max() <= 100


def test_priority_is_weighted_sum_of_factors():
    r = score_locations(*mk()).set_index("location_id")
    w = config.PRIORITY_WEIGHTS
    expected = sum(r.loc["A", f] * w[f] for f in FACTORS)
    assert r.loc["A", "priority_score"] == pytest.approx(expected, abs=0.1)


def test_bad_weights_rejected():
    with pytest.raises(ValueError):
        score_locations(*mk(), weights={**config.PRIORITY_WEIGHTS, "severity": 0.9})


def test_changing_weights_changes_scores():
    a = score_locations(*mk()).set_index("location_id").priority_score
    w = {"severity": 0.0, "safety_risk": 0.0, "traffic_impact": 0.0, "incident_frequency": 1.0, "local_context": 0.0}
    b = score_locations(*mk(), weights=w).set_index("location_id").priority_score
    assert not a.equals(b)


def test_escalation_rules_fire():
    loc, inc, _ = mk()
    e = evaluate_escalations(loc, inc).set_index("location_id")
    assert e.loc["A", "escalated"] and e.loc["C", "escalated"] and not e.loc["B", "escalated"]


def test_score_never_suppresses_escalation():
    """C has a low score but an unresolved critical injury: it must outrank non-escalated B."""
    r = score_locations(*mk()).set_index("location_id")
    assert r.loc["C", "tier"] == "Immediate review"
    assert r.loc["C", "rank"] < r.loc["B", "rank"]
    assert r.loc["B", "priority_score"] > 0  # B can score higher yet still rank below escalated C


def test_resolved_incidents_do_not_escalate():
    loc, inc, _ = mk()
    inc["resolved"] = 1
    assert not evaluate_escalations(loc, inc).escalated.any()
