"""Data-quality checks: find contradictions and gaps. Pure pandas, no UI."""
from dataclasses import dataclass
import pandas as pd
from . import config


@dataclass
class Finding:
    check: str
    table: str
    count: int
    total: int
    level: str       # "info" | "warning" | "critical"
    note: str
    next_step: str

    @property
    def share(self):
        return self.count / self.total if self.total else 0.0


def _level(share):
    return "info" if share == 0 else ("warning" if share < 0.2 else "critical")


def run_quality_checks(data) -> list:
    inc, com, loc = data.incidents, data.complaints, data.locations
    out = []

    n = int(((inc.resolved == 0) & inc.resolution_hours.notna()).sum())
    out.append(Finding("Unresolved incident has a resolution time", "incidents", n, len(inc),
        _level(n / len(inc)),
        "Incidents marked unresolved still carry resolution_hours, so one field is wrong.",
        "Confirm with the data owner which field is correct before using resolution times."))

    n = int((com.status.isin(config.OPEN_STATUSES) & com.days_to_resolution.notna()).sum())
    out.append(Finding("Open complaint has days_to_resolution", "complaints", n, len(com),
        _level(n / len(com)),
        "Complaints still open/assigned/in progress report a resolution time.",
        "Treat days_to_resolution as unreliable for open complaints."))

    n = int(((inc.injuries >= 2) & (inc.severity == "Low")).sum())
    out.append(Finding("Multiple injuries but severity Low", "incidents", n, len(inc),
        _level(n / len(inc)),
        "Severity may be under-recorded where people were injured.",
        "Verify severity by field inspection; safety rules use injuries directly."))

    sev = inc.assign(s=inc.severity.map(config.SEVERITY_ORDER)).groupby("injuries").s.mean()
    flat = (sev.max() - sev.min()) < 0.3
    out.append(Finding("Severity does not track injuries", "incidents", int(flat), 1,
        "warning" if flat else "info",
        "Mean severity barely changes as injuries rise, so severity labels carry little information.",
        "Do not rely on severity alone; combine with injuries and context."))

    per_loc = inc.groupby("location_id").size().reindex(loc.location_id, fill_value=0)
    few = int((per_loc < 5).sum())
    out.append(Finding("Locations with fewer than 5 incidents", "locations", few, len(loc),
        _level(few / len(loc)),
        "Rankings for locations with few records are statistically noisy.",
        "Shown as lower confidence; collect more reports or inspect."))

    span_days = (inc.timestamp.max() - inc.timestamp.min()).days
    out.append(Finding("Coverage period", "incidents", 0, 1, "info",
        f"{inc.timestamp.min():%Y-%m-%d} to {inc.timestamp.max():%Y-%m-%d} ({span_days} days) - "
        "only one year, so seasonal forecasting is not supported.", "None."))
    return out
