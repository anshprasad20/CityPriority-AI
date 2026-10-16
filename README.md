# CityPriority AI

**Explainable civic-issue prioritisation prototype for DATATHON 2026**

CityPriority AI ranks 1,000 simulated city locations by current maintenance/safety review priority. It combines five factors into a weighted score, applies separate hard safety-escalation rules, and provides plain-language explanations through an offline HTML dashboard.

> **Important:** All project data, including locations, coordinates, incidents, complaints, and timestamps, is synthetic demonstration data. This prototype is not validated for real-world public-safety or resource-allocation decisions. Escalations are leads for inspection, not confirmed hazards.

## Features

- Loads and validates location, incident, and public-complaint CSV files.
- Reports data-quality issues and missing/invalid values.
- Calculates an explainable priority score for each location.
- Applies three hard escalation rules independently of the weighted score.
- Exports ranked results to CSV.
- Builds a self-contained dashboard that works offline in a modern browser.
- Includes a map view using simulated coordinates, filters, location details, a what-if weighting tool, data-quality findings, and a methodology page.
- Includes automated tests for data loading and scoring.

## Project structure

```text
citypriority-ai/
├── run_stage1.py                 # Load data and report data quality
├── run_stage2.py                 # Calculate scores and apply escalation rules
├── run_model.py                  # Run the scoring pipeline and export ranked CSV
├── validate_model.py             # Compare forecasting baselines (scikit-learn/scipy)
├── export_dashboard_data.py       # Generate dashboard/dash_data.json
├── build_dashboard.py             # Build the final offline HTML dashboard
├── requirements.txt               # Full dependency set
├── requirements-minimal.txt       # Minimal dependencies for core workflow
├── core/
│   ├── config.py                 # Paths, factor weights, thresholds and categories
│   ├── loader.py                 # CSV loading and validation
│   ├── quality.py                # Data-quality checks
│   ├── scoring.py                # Weighted scoring, ranking and explanations
│   └── safety_rules.py            # Hard escalation rules
├── data/
│   ├── locations.csv
│   ├── incidents.csv
│   ├── public_complaints.csv
│   └── DATA_SOURCES.md
├── dashboard/
│   ├── dashboard_template.html    # Edit this source template
│   ├── dash_data.json             # Generated dashboard data
│   └── citypriority_dashboard.html # Generated, standalone dashboard
├── results/
│   └── ranked_locations.csv       # Example/exported ranking
├── tests/
│   ├── test_loader.py
│   └── test_scoring.py
├── DEMO_SCRIPT.md
└── HANDOFF_FOR_AI.txt
```

## Requirements

- Python 3.10 or newer recommended.
- Windows, macOS, or Linux.
- A modern browser to view the HTML dashboard.
- Internet is not required to open the built dashboard.

## Installation

### Windows (PowerShell or Command Prompt)

From the project directory:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
```

If `python` is not recognised, install Python from the official Python website and ensure it is added to PATH.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
```

Use `requirements.txt` instead if you need the larger optional stack. The forecasting validation script requires `scikit-learn` and `scipy`; install the full requirements if those are not included in the minimal file.

## Run the pipeline

Run commands from the `citypriority-ai` project directory.

### 1. Load and inspect the data

```bash
python run_stage1.py
```

This loads the CSV files and prints data-validation and quality information.

### 2. Calculate priority scores

```bash
python run_stage2.py
```

This calculates scores, applies hard escalation rules, and prints a short ranking/example explanation.

### 3. Export a ranked CSV

```bash
python run_model.py
```

By default, the output is written to `results/ranked_locations.csv`.

To choose a data folder or output path:

```bash
python run_model.py --data data --out results/ranked_locations.csv
```

The data folder should contain the expected location, incident, and complaint CSV files.

### 4. Run tests

```bash
python -m pytest -q
```

The repository includes tests for loading and scoring. Run them after making changes; do not assume they pass without running them.

### 5. Run the forecasting validation (optional)

```bash
python validate_model.py
```

This script requires `scikit-learn` and `scipy`. Existing validation found that the tested models did not outperform a simple average baseline on the synthetic data. The priority score should therefore be described as a **current-priority ranking**, not a prediction of future incidents.

## Build and open the dashboard

Run these commands in order:

```bash
python export_dashboard_data.py
python build_dashboard.py
```

Then open this file in a browser:

```text
dashboard/citypriority_dashboard.html
```

The generated dashboard is a single HTML file with its styling, JavaScript, and data embedded. It can be opened directly and does not require a local server or an internet connection.

**When changing the dashboard, edit `dashboard/dashboard_template.html`, not the generated `citypriority_dashboard.html`.** Re-run both build commands to regenerate the final dashboard.

## How prioritisation works

The prototype combines five factor scores (each on a 0–100 scale) using the configured weights:

| Factor | Weight | Notes |
|---|---:|---|
| Severity | 30% | Incident severity scoring |
| Safety risk | 25% | Safety-related signals |
| Traffic impact | 20% | Uses road type and traffic-related incident types as a proxy; actual traffic counts are unavailable |
| Incident frequency | 15% | Incident volume, with shrinkage for small samples |
| Local context | 10% | Context such as pedestrian activity and nearby sensitive sites |

Locations with small samples are pulled toward the city average to reduce the influence of sparse data. Weights and thresholds are configured in `core/config.py`.

### Hard safety-escalation rules

The escalation rules are applied independently of the weighted score. A location is escalated if it meets one of these configured conditions:

1. An unresolved Critical incident with at least one injury.
2. An unresolved High/Critical injury incident near a school or hospital with high pedestrian activity.
3. Unresolved incidents at one location total at least four injuries.

These rules are intended to flag locations for review. Because the data is synthetic and the resolution fields are unreliable, an escalation is **not evidence that a real hazard exists**.

## Dashboard sections

The dashboard includes:

- **Overview:** summary metrics and a snapshot of the ranking.
- **Priority list:** ranked locations, filters, and CSV export.
- **Map:** location points plotted using simulated latitude/longitude; no live street map is loaded.
- **Location:** score factors, explanation, incident mix, and caveats for a selected location.
- **What-if:** explore how changing factor weights affects the ranking.
- **Data quality:** known quality issues and validation results.
- **Method:** scoring factors, escalation rules, and limitations.

## Data and interpretation limitations

- All supplied project data is synthetic and must not be represented as real city data.
- Coordinates and timestamps are simulated.
- The data covers one year only (2025); it is not sufficient to establish seasonal patterns.
- There are no actual repair-cost estimates or traffic-count measurements.
- Traffic impact is a proxy based partly on road type and incident type.
- Current tests found no forecasting model that beats a simple average baseline on this data. The score ranks **current review priority**; it does not forecast future incidents.
- Severity has limited demonstrated relationship with outcomes in this synthetic dataset, despite its current 30% weight.
- All unresolved incidents and open complaints still have resolution-time values. Therefore, those fields cannot reliably confirm that work is complete, and escalation flags should be treated as leads for on-site verification.
- The map's background is illustrative; only plotted points come from the supplied dataset, and those coordinates are simulated.
- Any imagery that is watermarked or not licensed for reuse should be replaced with properly licensed assets before public distribution.

## Configuration

Edit `core/config.py` to adjust scoring weights, category mappings, score mappings, shrinkage, and escalation thresholds. Changes to weights or rules should be documented, tested, and clearly disclosed in demonstrations.

For dashboard appearance and behavior, edit `dashboard/dashboard_template.html`. The build script generates the final HTML and updates its build metadata/version according to the settings in `build_dashboard.py`.

## Demo guide

See [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) for a short walkthrough and suggested answers to common presentation questions.

## License

No license information was provided with this project. Add a suitable `LICENSE` file before redistributing the project or its assets.
