# CityPriority AI (Prototype)

Explainable civic-issue prioritisation (DATATHON 2026). **Data is SYNTHETIC. Not for real public-safety decisions.**
Ranks 1,000 city locations by current priority, with hard safety-escalation rules and a per-location explanation.

## Setup (Windows)
    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -r requirements-minimal.txt

(`requirements.txt` installs the larger stack; `validate_model.py` needs scikit-learn and scipy.)

## Run
    python run_stage1.py                 # load data + data-quality report
    python run_stage2.py                 # priority scores + safety escalation
    python run_model.py                  # score a data folder -> results/ranked_locations.csv
    python run_model.py --data PATH --out results.csv
    python -m pytest -q                  # 12 tests (all pass as of v1.0.0)
    python validate_model.py             # forecasting check (no model beats the average)

## Rebuild the dashboard
    python export_dashboard_data.py      # writes dashboard/dash_data.json
    python build_dashboard.py            # inlines the JSON -> dashboard/citypriority_dashboard.html

Open `dashboard/citypriority_dashboard.html` in any browser (fully offline, no install).
The **Map** tab plots every location by its (simulated) latitude/longitude with no internet needed.
Edit `dashboard/dashboard_template.html`, never the generated file.

## Version and footer
Current version: **1.0.0 (prototype)**. Every dashboard page ends with a footer showing the data source (DATATHON 2026 organisers),
"Synthetic data", the data coverage period, the build date and the version.
- The **build date** is filled in automatically each time you run `python build_dashboard.py`.
- The **version** is the `VERSION` constant at the top of `build_dashboard.py`; change it there when you ship a new one.

## Dashboard pages
Overview | Priority list | Map | Location | What-if | Data quality | Method.
The Map plots locations by their **simulated** latitude/longitude (offline, no street tiles). The What-if page shows, in plain words,
how many places each location moves when you change the weights.

## Demo
See `DEMO_SCRIPT.md` for a 60-90 second walkthrough and honest answers to likely judge questions.

## Method
Five factors (0-100) are combined: severity 30%, safety risk 25%, traffic impact 20% (proxy: road type),
incident frequency 15%, local context 10%. Small-sample locations are shrunk toward the city average.
Hard escalation rules (independent of the score) put a location first: R1 unresolved Critical incident with injury;
R2 unresolved High/Critical injury incident near a school/hospital with high pedestrian activity;
R3 unresolved incidents totalling 4+ injuries. 52 of 1,000 locations are escalated.

## Limitations
Synthetic data; no repair-cost or traffic-count data; one year only; the score ranks CURRENT priority and does not forecast;
every unresolved incident still lists a resolution time, so "unresolved" status needs on-site confirmation.

See `HANDOFF_FOR_AI.txt` for full project context.

## Look and feel (added in v1.1 work)
- Map: bigger, with a generated illustrative basemap (roads, river, parks, scale bar). Only the dots are real data.
- Branding: logo in the header and favicon (`dashboard/logo.b64`, `favicon.b64`).
- Patrol car and officer images (`dashboard/car.b64`, `officer.b64`) are inlined by `build_dashboard.py`.
- Loading screens and a corner helper use six cartoon characters (`dashboard/chars.json`); lines live in `CAST` in `dashboard_template.html`.
- Several images came from stock sheets with watermarks: replace with licensed versions before publishing.
