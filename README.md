# GeoVision

Satellite-based green cover monitoring and forecasting for **Kolkata (KMC, 141 wards)**, years **2018–2024**.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

GEE project ID is in `configs/city_aoi.yaml` (`gee_project`).

## Phase 0 — normalize wards

```powershell
python -m src.gee.normalize_wards
```

Writes `ward_id` on `data/raw/boundaries/wards.geojson` and dissolves `aoi.geojson`.

## Docs

- Build plan: `docs/agent-build-plan.md`
- Agent rules: `AGENTS.md`
