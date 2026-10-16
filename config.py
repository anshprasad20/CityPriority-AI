"""Central, editable configuration. No UI code here."""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FILES = {
    "locations": DATA_DIR / "locations.csv",
    "incidents": DATA_DIR / "incidents.csv",
    "complaints": DATA_DIR / "public_complaints.csv",
}

DATA_IS_SYNTHETIC = True
DATA_LABEL = "SYNTHETIC DEMONSTRATION DATA (DATATHON 2026). Not a real city."

# Required columns per table (loader fails loudly if any are missing).
REQUIRED_COLUMNS = {
    "locations": ["location_id", "zone", "road_type", "road_condition",
                  "population_density_per_km2", "near_school", "near_hospital",
                  "pedestrian_activity", "latitude", "longitude"],
    "incidents": ["incident_id", "location_id", "timestamp", "incident_type",
                  "severity", "injuries", "reported_by", "resolved", "resolution_hours"],
    "complaints": ["complaint_id", "location_id", "created_at", "category",
                   "priority_reported", "status", "days_to_resolution"],
}

# Allowed category values (anything else is reported as a validation issue).
ALLOWED = {
    ("incidents", "severity"): ["Low", "Medium", "High", "Critical"],
    ("incidents", "incident_type"): ["Pothole", "Streetlight outage", "Blocked drain",
                                     "Flooding", "Signal failure", "Collision"],
    ("complaints", "status"): ["Open", "Assigned", "In progress", "Resolved", "Closed"],
    ("complaints", "priority_reported"): ["Low", "Normal", "High"],
}
OPEN_STATUSES = ["Open", "Assigned", "In progress"]

SEVERITY_ORDER = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

# ASSUMPTION (editable): how incident types relate to complaint categories.
# 'Waste' and 'Pedestrian safety' complaints have no incident counterpart.
INCIDENT_TO_COMPLAINT_CATEGORY = {
    "Pothole": "Road damage",
    "Streetlight outage": "Lighting",
    "Blocked drain": "Drainage",
    "Flooding": "Drainage",
    "Signal failure": "Traffic",
    "Collision": "Traffic",
}

# Initial design weights (assumptions; configurable, to be validated).
PRIORITY_WEIGHTS = {"severity": 0.30, "safety_risk": 0.25, "traffic_impact": 0.20,
                    "incident_frequency": 0.15, "local_context": 0.10}

# ---- Stage 2: scoring ----
SHRINKAGE_K = 5            # pseudo-incidents pulling small-sample locations toward the city average
SEVERITY_POINTS = {"Low": 25, "Medium": 50, "High": 75, "Critical": 100}
ROAD_TYPE_SCORE = {"Highway": 100, "Arterial": 80, "Collector": 55, "Local": 30, "Residential": 20}
ROAD_CONDITION_SCORE = {"Critical": 100, "Poor": 70, "Fair": 40, "Good": 10}
PEDESTRIAN_SCORE = {"High": 1.0, "Medium": 0.5, "Low": 0.0}
TRAFFIC_INCIDENT_TYPES = ["Signal failure", "Collision"]

# Safety escalation thresholds (hard rules; independent of the weighted score).
ESCALATION = {
    "critical_with_injury_min_injuries": 1,
    "sensitive_site_min_injuries": 1,
    "unresolved_injuries_total": 4,
}
