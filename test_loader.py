import pandas as pd, pytest
from core.loader import load_data, DataValidationError
from core import config
from core.quality import run_quality_checks


def test_real_data_loads_and_joins():
    d = load_data()
    assert len(d.locations) == 1000 and len(d.incidents) == 10000 and len(d.complaints) == 8000
    assert d.issues == []
    assert d.synthetic is True


def test_missing_column_fails_loudly(tmp_path):
    for k, p in config.FILES.items():
        df = pd.read_csv(p)
        if k == "incidents":
            df = df.drop(columns=["severity"])
        df.to_csv(tmp_path / p.name, index=False)
    files = {k: tmp_path / p.name for k, p in config.FILES.items()}
    with pytest.raises(DataValidationError):
        load_data(files)


def test_orphan_location_is_reported(tmp_path):
    for k, p in config.FILES.items():
        df = pd.read_csv(p)
        if k == "incidents":
            df.loc[0, "location_id"] = "L9999"
        df.to_csv(tmp_path / p.name, index=False)
    files = {k: tmp_path / p.name for k, p in config.FILES.items()}
    assert any("unknown location_id" in i for i in load_data(files).issues)


def test_quality_checks_find_known_contradictions():
    f = {x.check: x for x in run_quality_checks(load_data())}
    assert f["Unresolved incident has a resolution time"].count > 0
    assert f["Open complaint has days_to_resolution"].count > 0
