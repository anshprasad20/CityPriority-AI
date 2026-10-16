"""Load and validate the three CSV tables. Missing values stay NaN (never invented)."""
from dataclasses import dataclass, field
import pandas as pd
from . import config


class DataValidationError(Exception):
    """Raised when the data cannot be used at all (missing file/columns)."""


@dataclass
class CityData:
    locations: pd.DataFrame
    incidents: pd.DataFrame
    complaints: pd.DataFrame
    issues: list = field(default_factory=list)  # non-fatal validation messages
    synthetic: bool = config.DATA_IS_SYNTHETIC


def _read(name, path):
    if not path.exists():
        raise DataValidationError(f"Missing file for '{name}': {path}")
    df = pd.read_csv(path)
    missing = [c for c in config.REQUIRED_COLUMNS[name] if c not in df.columns]
    if missing:
        raise DataValidationError(f"'{name}' is missing required columns: {missing}")
    return df


def load_data(files=None) -> CityData:
    files = files or config.FILES
    loc = _read("locations", files["locations"])
    inc = _read("incidents", files["incidents"])
    com = _read("complaints", files["complaints"])

    inc["timestamp"] = pd.to_datetime(inc["timestamp"], errors="coerce")
    com["created_at"] = pd.to_datetime(com["created_at"], errors="coerce")

    issues = []
    tables = {"locations": loc, "incidents": inc, "complaints": com}
    ids = {"locations": "location_id", "incidents": "incident_id", "complaints": "complaint_id"}

    for name, df in tables.items():
        dup = int(df[ids[name]].duplicated().sum())
        if dup:
            issues.append(f"{name}: {dup} duplicate {ids[name]} values")
    for name in ("incidents", "complaints"):
        orphans = int((~tables[name]["location_id"].isin(loc["location_id"])).sum())
        if orphans:
            issues.append(f"{name}: {orphans} rows reference unknown location_id")
    for col in ("timestamp",):
        bad = int(inc[col].isna().sum())
        if bad:
            issues.append(f"incidents: {bad} unparseable {col} values")
    bad = int(com["created_at"].isna().sum())
    if bad:
        issues.append(f"complaints: {bad} unparseable created_at values")
    for (tname, col), allowed in config.ALLOWED.items():
        vals = tables[tname][col].dropna()
        unexpected = sorted(set(vals) - set(allowed))
        if unexpected:
            issues.append(f"{tname}.{col}: unexpected values {unexpected}")
    return CityData(loc, inc, com, issues)
