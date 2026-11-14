# Agent Build Plan — Satellite-Based Green Cover Monitoring and Forecasting System

**Student:** Debayan Sarkar  
**Document role:** Single definitive build plan for Debayan (beginner) **and** any AI coding agent  
**Plan date:** 2026-11-13  
**Status:** LOCKED for execution  

**City supersession (read once):** Older docs ([`concrete-finish-plan.md`](./concrete-finish-plan.md), [`green-cover-fyp-plan.md`](./green-cover-fyp-plan.md)) recommended **Bengaluru** as a placeholder. **This plan locks Kolkata (KMC)** instead. City choice only changes AOI + ward polygons; the rest of the pipeline is identical. Use this file as the source of truth for city and phase order.

**Companion docs (do not invent conflicting scope):**
| Doc | Role |
|---|---|
| [`Project_Synopsis_...pdf`](./Project_Synopsis_Satellite-Based_Green_Cover_Monitoring_and_Forecasting_System.pdf) | Scope & objectives |
| [`concrete-finish-plan.md`](./concrete-finish-plan.md) | Locked free stack + week calendar |
| [`green-cover-fyp-plan.md`](./green-cover-fyp-plan.md) | Architecture & module detail |
| [`beginner-model-training-guide.md`](./beginner-model-training-guide.md) | NDVI → labels → U-Net order |

**Hard constraints:** Free stack only (GEE, Colab, Streamlit). No paid imagery. No ease-care / monorepo edits. Agents ship code/configs/checklists; Debayan owns every Google login, GEE export, Colab GPU run, and visual QC.

---

## 1. Project one-pager

### Problem
Cities lose greenery in small patches that ground surveys miss. Planners lack up-to-date ward maps, links from green loss to heat/pollution, and simple “what if” tools.

### Goal (one line)
Show **where** Kolkata is losing greenery, **why** it matters (heat, pollution), and **what happens next** if nothing changes — via an interactive dashboard.

### Users
| Who | Needs from the demo |
|---|---|
| Municipal / urban planners | Ward green %, loss hotspots, priority zones, scenario compare |
| Env / forest departments | Before/after encroachment evidence |
| Public health | Heat / pollution vs green at ward level |
| Citizens / NGOs | Transparent ward green trends |
| Examiners | Reproducible pipeline, metrics tables, honest limitations |

### Success = demo checklist (print & tick)

- [ ] AOI stated: **Kolkata (KMC), 141 wards**, years **2018–2024**
- [ ] City green-% trend chart (≥6 years)
- [ ] LULC map year A vs year B (4 classes)
- [ ] Change map + top-5 green-loss wards
- [ ] Forecast vs held-out year + 3-model metrics + uncertainty bands
- [ ] LST–green scatter (Pearson r, p)
- [ ] NO₂ or aerosol vs green (ward level)
- [ ] Priority wards ranked + one scenario Δ green %
- [ ] Live Streamlit Community Cloud URL: time slider + CSV export
- [ ] Limitations said aloud (10 m, open labels, no legal enforcement)

**Pass rule:** every box above has a figure/table **or** a live click in the dashboard.

---

## 2. Locked decisions (single source of truth)

### 2.1 City — LOCKED: Kolkata (KMC)

| Field | Value |
|---|---|
| **City** | **Kolkata Municipal Corporation (KMC)** |
| **Wards** | **141** polygons |
| **Why locked** | Preferred city; ward polygons **verified usable** (see below). No blocker. |
| **Backup city** | Bengaluru (BBMP) — only if Kolkata wards later prove corrupt for area calc; pipeline unchanged |

**Ward GeoJSON confirmation (2026-11-13):**

| Source | Format | Status |
|---|---|---|
| **DataMeet** `Municipal_Spatial_Data/Kolkata/kolkata.geojson` | GeoJSON, ~2.8 MB, 141 features, attr `WARD` | **Primary — verified HTTP 200, FeatureCollection, 0 blank WARD** |
| OpenCity “Kolkata Wards Map 2022” | KML (~2.3 MB), public domain | Backup / cross-check |
| Bharatlas wards_kolkata | GeoJSON / Parquet, 141 wards, ODbL, sourced from OpenCity | Alternate download |

**Canonical download URL (primary):**  
`https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Kolkata/kolkata.geojson`

**Rough AOI bbox (from DataMeet file):** lon **88.24–88.46**, lat **22.45–22.63**. Map center ≈ `(22.54, 88.35)`.

### 2.2 Years, season, classes

| Item | Locked value |
|---|---|
| Years | **2018, 2019, 2020, 2021, 2022, 2023, 2024** (7 years) |
| Season window | Post-monsoon **Oct 1 → Feb 28** (end year = start year + 1) |
| Classes | `0 vegetation`, `1 built-up`, `2 water`, `3 barren` |
| Resolution (optical) | Sentinel-2 **10 m** |
| Tile size | **256×256** |

### 2.3 Tech stack (do not swap mid-FYP)

| Layer | Locked primary |
|---|---|
| Data access | Google Earth Engine (`earthengine-api` + `geemap`) |
| Optical | `COPERNICUS/S2_SR_HARMONIZED` |
| Heat (LST) | Landsat 8/9 C2 L2 `ST_B10` |
| Pollution | Sentinel-5P OFFL NO₂ (+ aerosol optional) |
| Labels | ESA WorldCover v200 primary; Dynamic World second opinion |
| Boundaries | KMC ward GeoJSON (DataMeet primary) |
| Geo stack | rasterio + GeoPandas + NumPy + scikit-learn |
| Segmentation | PyTorch + `segmentation_models_pytorch` U-Net (ResNet34) |
| Forecast | Persistence + CA-Markov + ConvLSTM (all three compared) |
| Dashboard | Streamlit + Folium (`streamlit-folium`) + Plotly |
| Thin API | FastAPI reading precomputed files (optional until polish) |
| Compute | Google Colab T4; Kaggle GPU backup |
| Live demo | **Streamlit Community Cloud** |

### 2.4 Must vs Should vs Nice

| Priority | Items | Target phase |
|---|---|---|
| **Must** | Mapping, U-Net + baselines, change, forecast comparison (3 approaches attempted), core metrics | End Phase 7 |
| **Should (credibility pack — later phases)** | LST + pollution; **ward priority score**; **what-if scenarios**; **forecast uncertainty bands**; **live Streamlit Community Cloud demo** | Phases 8–11 |
| **Nice** | GAN, alerts, planting recommender, carbon estimate, rich API, second city | Phase 12 only if Must green |

---

## 3. Repo layout (exact tree)

Create a **new** repo/folder `green-cover-fyp/` (not inside ease-care):

```text
green-cover-fyp/
├── README.md
├── requirements.txt
├── .gitignore                    # ignore data/raw, data/interim, *.tif, models/*.pt, .venv
├── configs/
│   ├── city_aoi.yaml             # LOCKED Kolkata params
│   ├── class_map.yaml            # WorldCover → 0..3 remap
│   └── priority_weights.yaml     # later: priority score weights
├── data/
│   ├── raw/
│   │   ├── s2/                   # s2_median_{year}.tif
│   │   ├── lst/                  # lst_{year}.tif
│   │   ├── s5p/                  # no2_{year}.tif
│   │   ├── labels/               # worldcover_remapped_{year}.tif
│   │   └── boundaries/
│   │       ├── wards.geojson     # 141 KMC wards
│   │       ├── aoi.geojson       # dissolve of wards
│   │       └── SOURCE.md         # URL, date, licence
│   ├── interim/
│   │   ├── tiles/images/         # t_XXXX.npy (6,256,256)
│   │   ├── tiles/masks/          # t_XXXX.npy (256,256) uint8
│   │   ├── tiles/manifest.csv
│   │   └── labels_verified/      # hand-fixed tiles (optional)
│   └── processed/
│       ├── ndvi/                 # ndvi_{year}.tif
│       ├── indices/              # optional multi-index stacks
│       ├── lulc/                 # lulc_{year}.tif
│       ├── change/               # change_{y0}_{y1}.tif
│       ├── forecast/             # forecast_{model}_{year}.tif + uncertainty
│       ├── impact/               # ward impact columns merge
│       ├── decision/             # priority + scenario outputs
│       └── stats/                # ward_year.parquet / .csv
├── src/
│   ├── gee/                      # export_s2_yearly.py, export_lst.py, export_s5p.py, export_labels.py
│   ├── preprocess/               # align.py, tile.py
│   ├── indices/                  # compute.py, ward_green.py
│   ├── classify/                 # remap_labels.py, train_rf.py, train_unet.py, infer_lulc.py
│   ├── change/                   # detect.py, ward_rank.py
│   ├── forecast/                 # persistence.py, ca_markov.py, convlstm.py, uncertainty.py
│   ├── impact/                   # correlate.py
│   ├── decision/                 # priority.py, scenarios.py
│   ├── api/                      # main.py (FastAPI, thin)
│   └── dashboard/                # app.py (Streamlit)
├── notebooks/
│   ├── 01_week1_ndvi.ipynb
│   ├── train_unet_colab.ipynb
│   └── train_convlstm_colab.ipynb
├── models/                       # unet_best.pt, convlstm_best.pt (gitignored)
├── reports/
│   ├── figures/
│   └── tables/
├── docs/
│   ├── study_area.md
│   ├── DEMO_SCRIPT.md
│   └── metrics_log.md
└── tests/
    ├── test_ndvi.py
    ├── test_change_rules.py
    └── test_green_fraction.py
```

---

## 4. Data contracts

Agents and humans must follow these names. Breaking them breaks the dashboard.

### 4.1 CRS

| Use | CRS |
|---|---|
| Exchange / GeoJSON / GEE export default | **EPSG:4326** (CRS84) |
| Area / hectares | **EPSG:32645** (UTM 45N — Kolkata) |
| All yearly rasters | Same grid after align (10 m, shared transform) |

### 4.2 Raster naming

| Asset | Path pattern | Dtype / bands |
|---|---|---|
| S2 median | `data/raw/s2/s2_median_{year}.tif` | float reflectance-like; bands **B2,B3,B4,B8,B11,B12** in that order |
| NDVI | `data/processed/ndvi/ndvi_{year}.tif` | float32, 1 band |
| Labels remapped | `data/raw/labels/worldcover_remapped_{year}.tif` | uint8, values {0,1,2,3} |
| LULC predict | `data/processed/lulc/lulc_{year}.tif` | uint8 {0,1,2,3}; nodata=255 |
| Change | `data/processed/change/change_{y0}_{y1}.tif` | uint8: 0=unchanged, 1=loss, 2=gain |
| Forecast | `data/processed/forecast/{model}_lulc_{year}.tif` | same as LULC |
| Uncertainty | `data/processed/forecast/{model}_unc_{year}.tif` | float32 band (e.g. std of green-prob or ensemble disagreement) |
| LST | `data/raw/lst/lst_{year}.tif` | float32 °C |
| NO₂ | `data/raw/s5p/no2_{year}.tif` | float32 seasonal mean |

### 4.3 Class IDs

| ID | Name | WorldCover groups (document exact codes in `configs/class_map.yaml`) |
|---|---|---|
| 0 | vegetation | tree, shrubland, grassland, cropland, mangrove, moss/lichen (+ wetland if green-focused) |
| 1 | built-up | built-up |
| 2 | water | permanent water (+ snow/ice if any) |
| 3 | barren | bare / sparse vegetation |

### 4.4 Vector / ward attributes

| File | Required attributes after normalize |
|---|---|
| `data/raw/boundaries/wards.geojson` | `ward_id` (string/int, unique, from source `WARD`), geometry Polygon/MultiPolygon |
| `data/raw/boundaries/aoi.geojson` | single (Multi)Polygon = dissolve of wards |
| `data/processed/stats/ward_year.parquet` | `ward_id`, `year`, `green_pct`, `built_pct`, `water_pct`, `barren_pct`, `area_ha`, plus later: `lst_mean`, `no2_mean`, `priority_score`, `loss_ha` |

**Normalize rule:** on first ingest, rename DataMeet `WARD` → `ward_id`, reproject copy for area to UTM 45N, write `SOURCE.md` with URL + download date + licence (DataMeet CC-BY-4.0 unless file says otherwise).

### 4.5 Config skeleton (`configs/city_aoi.yaml`)

```yaml
city: "kolkata"
city_full: "Kolkata Municipal Corporation (KMC)"
n_wards: 141
crs_export: "EPSG:4326"
crs_area: "EPSG:32645"          # UTM 45N
bbox: [88.24, 22.45, 88.46, 22.63]   # lon_min, lat_min, lon_max, lat_max
map_center: [22.54, 88.35]      # lat, lon for Folium
years: [2018, 2019, 2020, 2021, 2022, 2023, 2024]
season_start: "10-01"
season_end: "02-28"
bands: ["B2", "B3", "B4", "B8", "B11", "B12"]
cloud_pct_max: 40
scale_m: 10
tile_size: 256
classes: ["vegetation", "built-up", "water", "barren"]
ndvi_green_threshold: 0.35
held_out_forecast_year: 2024
train_years_forecast: [2018, 2019, 2020, 2021, 2022, 2023]
gee_project: "YOUR_GEE_PROJECT"   # Debayan fills
drive_folder: "green_cover_fyp"
wards_source_url: "https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Kolkata/kolkata.geojson"
```

---

## 5. Phased build (Phases 0–12 ≈ 12 weeks)

**How to use:** finish one phase’s Acceptance tests before starting the next.  
**Human** = Debayan must do (login / export / eyes).  
**Agent** = AI coding agent builds in the repo.

---

### Phase 0 — Accounts, city lock, repo skeleton

**Goal:** GEE works; Kolkata wards on disk; repo tree + config committed.

| | |
|---|---|
| **Inputs** | Google account; this plan; DataMeet wards URL |
| **Outputs** | `green-cover-fyp/` tree; `configs/city_aoi.yaml`; `data/raw/boundaries/{wards,aoi}.geojson`; `docs/study_area.md`; `data/raw/boundaries/SOURCE.md` |

**Human steps**
1. Register / confirm [Google Earth Engine](https://earthengine.google.com/); note Cloud **project ID**.
2. Install Python 3.11+, Git, QGIS (or plan to use geemap only).
3. Download wards GeoJSON from DataMeet URL → save as `data/raw/boundaries/wards.geojson`.
4. Open wards in QGIS; confirm 141 polygons; write 5-line study-area note.
5. Run `earthengine authenticate` (or Colab `ee.Authenticate()`).

**Agent steps**
1. Create exact folder tree (§3) + `.gitignore` + `requirements.txt` + `README.md`.
2. Write `configs/city_aoi.yaml` (Kolkata locked) and `configs/class_map.yaml` stub.
3. Script `src/gee/normalize_wards.py`: rename `WARD`→`ward_id`, dissolve → `aoi.geojson`, write bbox check.
4. Fill `docs/study_area.md` template (city, CRS, years, ward source).

**Commands / scripts to create**
- `src/gee/normalize_wards.py`
- `configs/city_aoi.yaml`, `configs/class_map.yaml`

**Acceptance tests**
- [ ] `python -c "import ee; ee.Initialize(project='...'); print('GEE OK')"` succeeds (Human).
- [ ] Wards file has 141 features and `ward_id`.
- [ ] `aoi.geojson` exists and covers wards.
- [ ] Config `city: kolkata`, `crs_area: EPSG:32645`.

**Done definition:** GEE auth OK; Kolkata AOI + wards committed paths documented; repo skeleton ready.

**Stop-if-blocked:** GEE registration pending → wait (do not swap city). Wards file corrupt → try OpenCity KML→GeoJSON or Bharatlas; only then consider Bengaluru backup with written reason in `study_area.md`.

---

### Phase 1 — First mosaic + NDVI (Week 1)

**Goal:** One year Sentinel-2 export + NDVI screenshot proving the pipeline.

| | |
|---|---|
| **Inputs** | AOI; GEE project; Phase 0 config |
| **Outputs** | `data/raw/s2/s2_median_2023.tif` (or any one year); `data/processed/ndvi/ndvi_2023.tif`; `reports/figures/week1_ndvi.png` |

**Human steps**
1. Upload `aoi.geojson` to GEE Assets **or** use bbox from config.
2. Run export script; monitor [Tasks](https://code.earthengine.google.com/tasks); download GeoTIFF from Drive → `data/raw/s2/`.
3. Visually check true-color (B4,B3,B2) in QGIS/Colab.

**Agent steps**
1. Write `src/gee/export_s2_one_year.py` and `src/gee/export_s2_yearly.py` (loop 2018–2024).
2. Write `src/indices/compute.py` (NDVI/EVI/NDBI/NDWI/NDMI) + `tests/test_ndvi.py`.
3. Write `src/indices/week1_ndvi.py` to write NDVI GeoTIFF + print rough green fraction.
4. Notebook `notebooks/01_week1_ndvi.ipynb` for Colab path.

**Commands / scripts**
- `src/gee/export_s2_one_year.py`, `src/gee/export_s2_yearly.py`
- `src/indices/compute.py`, `src/indices/week1_ndvi.py`
- `tests/test_ndvi.py`

**Acceptance tests**
- [ ] One S2 GeoTIFF opens; 6 bands; covers AOI.
- [ ] NDVI min/max sane (roughly −1..1); figure saved.
- [ ] Unit test for NDVI formula passes.

**Done definition:** Authenticated exports work; ≥1 mosaic + NDVI on disk.

**Stop-if-blocked:** Export `maxPixels` / size errors → clip tighter to AOI, export fewer bands first. Empty composite → loosen cloud filter or widen season slightly; document change.

---

### Phase 2 — Multi-year indices + ward green %

**Goal:** City + ward green % CSV for ≥6 years (threshold method).

| | |
|---|---|
| **Inputs** | Yearly S2 TIFFs; wards |
| **Outputs** | `data/processed/ndvi/ndvi_{year}.tif`; `data/processed/stats/ward_year.csv` (threshold columns); `reports/figures/city_green_trend.png` |

**Human steps**
1. Kick remaining yearly GEE exports; download all to `data/raw/s2/`.
2. Spot-check 2–3 years for cloud holes.

**Agent steps**
1. Batch NDVI + green fraction scripts.
2. `src/indices/ward_green.py`: zonal stats in UTM 45N; write CSV/Parquet.
3. Plot city trend; threshold sensitivity note (`ndvi_green_threshold` in config).

**Acceptance tests**
- [ ] ≥6 years in `ward_year` table with `green_pct`.
- [ ] Trend chart in `reports/figures/`.
- [ ] Areas computed in EPSG:32645 (not raw degrees).

**Done definition:** Threshold green-% story works without any neural net.

**Stop-if-blocked:** Missing year → still proceed with available years; note gap; do not invent values.

---

### Phase 3 — Labels + tiles

**Goal:** Remapped 4-class labels + ≥200 train / ≥40 val spatial tiles.

| | |
|---|---|
| **Inputs** | One (or more) S2 year; WorldCover via GEE |
| **Outputs** | `worldcover_remapped_*.tif`; `data/interim/tiles/{images,masks}/`; `manifest.csv` |

**Human steps**
1. Export WorldCover clip for AOI (agent provides script).
2. Visual QC in QGIS: park, dense core, Hooghly water — fix obvious errors into `labels_verified/` if needed.
3. Confirm band order matches masks spatially (overlay).

**Agent steps**
1. `src/gee/export_labels.py` + `src/classify/remap_labels.py` using `class_map.yaml`.
2. `src/preprocess/align.py` + `src/preprocess/tile.py` (256, skip mostly-nodata).
3. Spatial train/val split (~80/20); write `manifest.csv`.

**Acceptance tests**
- [ ] Masks only contain {0,1,2,3}.
- [ ] ≥200 train + ≥40 val tiles; paths in manifest resolve.
- [ ] Side-by-side RGB vs mask screenshots for 3 sites.

**Done definition:** Tiles load; visual QC done on park / core / water.

**Stop-if-blocked:** Label–image misalignment → fix CRS/transform before any training. Do **not** start U-Net.

---

### Phase 4 — U-Net + RF baseline

**Goal:** Train U-Net on Colab; beat or match RF/NDVI on val IoU; one full-year LULC map.

| | |
|---|---|
| **Inputs** | Tiles + manifest |
| **Outputs** | `models/unet_best.pt`; `reports/tables/seg_metrics.csv`; `data/processed/lulc/lulc_{year}.tif`; train curves figure |

**Human steps**
1. Upload tiles zip or Drive folder; open `train_unet_colab.ipynb`.
2. Runtime → GPU; run cells; confirm checkpoint saves.
3. Visual check 5–10 val predictions (trust maps over numbers).

**Agent steps**
1. Complete Colab notebook (dataset, U-Net ResNet34, Dice+Focal, mean IoU) per beginner guide.
2. `src/classify/train_rf.py` baseline on same val tiles.
3. `src/classify/infer_lulc.py` windowed inference → GeoTIFF.
4. Metrics table: IoU/F1/OA vs NDVI threshold vs RF vs U-Net.

**Acceptance tests**
- [ ] `unet_best.pt` exists with logged `val_iou`.
- [ ] Metrics table in `reports/tables/`.
- [ ] At least one citywide `lulc_YYYY.tif` opens in QGIS.
- [ ] U-Net ≥ RF on mean IoU **or** honest write-up why not.

**Done definition:** Segmentation story defensible for viva.

**Stop-if-blocked:** All-one-class predictions → fix labels/class weights/LR (see beginner guide). Colab GPU capped → switch to Kaggle; same notebook.

---

### Phase 5 — Multi-year LULC + change

**Goal:** Infer all years; gain/loss/unchanged; ward loss top-10; ≥50 verified change samples.

| | |
|---|---|
| **Inputs** | `unet_best.pt`; all yearly S2 |
| **Outputs** | `lulc_{year}.tif` for all years; `change_2018_2024.tif` (or chosen pair); ward loss ranking; sample CSV |

**Human steps**
1. Run inference jobs (Colab/CPU) for each year.
2. Hand-verify ≥50 change samples (true loss/gain/unchanged) → `reports/tables/change_samples.csv`.

**Agent steps**
1. Batch `infer_lulc.py` over years.
2. `src/change/detect.py` (veg→built = loss; non-veg→veg = gain).
3. `src/change/ward_rank.py` → top loss wards; figures.

**Acceptance tests**
- [ ] Change map + top-10 table in `reports/`.
- [ ] Precision/recall on ≥50 samples logged.
- [ ] `ward_year` updated with `loss_ha` where applicable.

**Done definition:** Change story with numbers + map.

**Stop-if-blocked:** Year with bad clouds → exclude from change pair; document. Do not invent change.

---

### Phase 6 — Forecast baselines (persistence + CA-Markov)

**Goal:** Two classical forecasts + held-out year green-% RMSE/MAE.

| | |
|---|---|
| **Inputs** | Multi-year LULC; config `held_out_forecast_year: 2024` |
| **Outputs** | `forecast/persistence_lulc_2024.tif`; `forecast/ca_markov_lulc_2024.tif`; comparison table |

**Human steps**
1. Confirm held-out year choice with mentor if needed (default 2024).
2. Visual check forecast vs actual LULC.

**Agent steps**
1. `src/forecast/persistence.py`.
2. `src/forecast/ca_markov.py` (transition matrix + simple suitability + CA allocation).
3. Metrics: OA/kappa on map; **RMSE/MAE of ward green %**.

**Acceptance tests**
- [ ] Two-model comparison table saved.
- [ ] Ward green-% RMSE/MAE computed vs held-out actual.

**Done definition:** Forecast baselines ship even if DL forecast fails later.

**Stop-if-blocked:** Too few years → still run persistence + CA-Markov; shorten claim horizon in report.

---

### Phase 7 — ConvLSTM + hard gate (Must complete)

**Goal:** Attempt ConvLSTM; compare three approaches; freeze forecast story.

| | |
|---|---|
| **Inputs** | Tile sequences of past LULC / class probs |
| **Outputs** | `convlstm_best.pt` **or** failure notes; 3-row metrics table; decision recorded in `docs/metrics_log.md` |

**Human steps**
1. Run ConvLSTM Colab training; checkpoint often.
2. With mentor/agent notes: accept primary forecast model for demo.

**Agent steps**
1. `notebooks/train_convlstm_colab.ipynb` + `src/forecast/convlstm.py`.
2. Unified eval script writing `reports/tables/forecast_comparison.csv`.
3. If unstable: document failure modes; set primary = CA-Markov or persistence — **still Must-complete**.

**Acceptance tests**
- [ ] Table has **Persistence | CA-Markov | ConvLSTM** (ConvLSTM may be “failed / experimental”).
- [ ] Hard-gate note written: which model is demo-primary.

**Done definition:** Month-3/Week-7 gate met: mapping + segmentation + change + forecasting comparison.

**Stop-if-blocked:** ConvLSTM diverges → **stop polishing DL**; ship two baselines + honest notes. Do not delay Phase 8+.

---

### Phase 8 — Impact (LST + pollution)

**Goal:** Correlate green with heat and one pollution indicator.

| | |
|---|---|
| **Inputs** | Ward green %; GEE Landsat LST; S5P NO₂ |
| **Outputs** | `data/raw/lst/`, `data/raw/s5p/`; scatter plots; `ward_year` columns `lst_mean`, `no2_mean`; r, p in table |

**Human steps**
1. Run GEE LST/S5P export scripts; download.
2. Sanity-check units (°C, NO₂ tropospheric column).

**Agent steps**
1. `src/gee/export_lst.py`, `src/gee/export_s5p.py`.
2. `src/impact/correlate.py` (Pearson r, p); figures.

**Acceptance tests**
- [ ] LST–green scatter with r, p.
- [ ] NO₂ or aerosol vs green at **ward** level (not park scale).

**Done definition:** Impact story with statistical numbers.

**Stop-if-blocked:** S5P too coarse → aggregate wards / boroughs; still report. Missing LST pixels → seasonal median + QA filter.

---

### Phase 9 — Credibility pack A: ward priority score + what-if scenarios

> **Explicit later phase — do not start before Phases 0–7 Must metrics exist.**

**Goal:** Rank wards for intervention; run BAU vs one intervention.

| | |
|---|---|
| **Inputs** | `ward_year` with green, LST, built, optional pop; forecast primary model |
| **Outputs** | `data/processed/decision/priority_wards.csv`; `priority_map` figure; scenario GeoJSON/raster; Δ green % table |

**Human steps**
1. Choose **one** scenario polygon (e.g. protect Maidan / plant a barren fringe) — draw GeoJSON.
2. Confirm weight defaults with mentor (`configs/priority_weights.yaml`).

**Agent steps**
1. `src/decision/priority.py`:  
   `score = w1*(1-green) + w2*lst_norm + w3*built + w4*pop_density` (normalize 0–1; document weights).
2. `src/decision/scenarios.py`: BAU vs protect (force veg persistence) **or** plant (barren→veg mask); re-run lightweight forecast; compute city/ward Δ green %.
3. Export ranked table + before/after figure.

**Acceptance tests**
- [ ] Top-10 priority wards table.
- [ ] Scenario shows numeric Δ green % (city and/or ward).
- [ ] Weights documented (not hidden magic).

**Done definition:** Decision-support slides ready.

**Stop-if-blocked:** No population grid → drop pop term; keep 3-factor score. Scenario engine slow → precompute two rasters instead of live sim.

---

### Phase 10 — Credibility pack B: forecast uncertainty bands

> **Explicit later phase — after a primary forecast exists.**

**Goal:** Show “how sure?” for examiners (ensemble or MC dropout).

| | |
|---|---|
| **Inputs** | Primary forecast model; optional ConvLSTM checkpoint |
| **Outputs** | `*_unc_2024.tif`; ward green-% prediction intervals or ± bands on chart; short methods note |

**Human steps**
1. Run multi-seed or MC-dropout inference jobs.
2. Approve legend wording (“ensemble std” / “MC dropout”).

**Agent steps**
1. `src/forecast/uncertainty.py`: ≥5-run ensemble **or** MC dropout on ConvLSTM; for CA-Markov, bootstrap transition matrix.
2. Plot ward green % with uncertainty band vs actual held-out year.
3. Add layer hook for dashboard (precomputed).

**Acceptance tests**
- [ ] Uncertainty raster or table exists.
- [ ] Chart with bands in `reports/figures/`.
- [ ] One paragraph in `docs/metrics_log.md` explaining method.

**Done definition:** Uncertainty visible in report + ready for dashboard.

**Stop-if-blocked:** DL ensemble too heavy → bootstrap CA-Markov / multi-threshold persistence only; still counts.

---

### Phase 11 — Credibility pack C: Streamlit app + live Community Cloud demo

> **Explicit later phase — productize only after precomputed rasters/tables exist.**

**Goal:** Mentor can click a **public URL** without Colab.

| | |
|---|---|
| **Inputs** | Precomputed LULC, change, forecast, uncertainty, priority, scenario, `ward_year` |
| **Outputs** | `src/dashboard/app.py`; `requirements.txt` pinned; **live Streamlit Community Cloud URL**; optional thin FastAPI |

**Human steps**
1. Push repo to **his** GitHub (large rasters via Drive links / sample tiles in repo).
2. Deploy on [Streamlit Community Cloud](https://streamlit.io/cloud); OAuth to his repo.
3. Click through demo checklist on the live URL.

**Agent steps**
1. Build Streamlit: map (Folium) + **year slider** + layers (NDVI/LULC/change/forecast/uncertainty/priority) + ward chart + scenario toggle + CSV download.
2. **No live GEE calls** in the app — read `data/processed/` only.
3. Optional `src/api/main.py` stub for `/v1/green-cover`.
4. `docs/DEMO_SCRIPT.md` (≤10 min).
5. Deploy config (`packages.txt` / secrets none).

**Acceptance tests**
- [ ] Local `streamlit run src/dashboard/app.py` works.
- [ ] **Live Community Cloud URL** loads; slider + CSV export work.
- [ ] Mentor dry-run without Debayan driving Colab.

**Done definition:** Live demo URL on the checklist.

**Stop-if-blocked:** Full rasters too big for Cloud → ship COG subsets / PNG overlays + full data on Drive; document. Auth issues → Human-only fix.

---

### Phase 12 — Polish, freeze, viva pack

**Goal:** Crash-free demo; metrics final; tag `v1.0-demo`.

| | |
|---|---|
| **Inputs** | Everything above |
| **Outputs** | Report chapters outline filled; PPT outline; known-bugs list; git tag; backup screen recording |

**Human steps**
1. Full dry run with DEMO_SCRIPT; record 2-min backup video.
2. Freeze figures; zip viva package.

**Agent steps**
1. Fill report/PPT outlines from `green-cover-fyp-plan.md` §§8.
2. Smoke tests: NDVI, change rules, dashboard import.
3. Nice-only if Must green: alerts / carbon / second-city smoke — **otherwise skip**.

**Acceptance tests**
- [ ] Demo checklist 100% ticked.
- [ ] `reports/tables/` metrics final.
- [ ] Known bugs listed; tag `v1.0-demo`.

**Done definition:** Viva-ready package.

**Stop-if-blocked:** Wi-Fi risk → rely on screen recording; still ship.

---

## 6. Core ML path (order is mandatory)

```text
NDVI threshold green %
    → WorldCover/Dynamic World labels (4 classes) + tiles
        → RF baseline + U-Net (ResNet34)
            → Multi-year LULC
                → Change (gain/loss)
                    → Persistence + CA-Markov
                        → ConvLSTM attempt
                            → (later) uncertainty / priority / scenarios / Streamlit
```

| Stage | Where | Deep learning? |
|---|---|---|
| A. NDVI | Phases 1–2 | No |
| B. Labels + tiles | Phase 3 | No |
| C. U-Net (+ RF) | Phase 4 | Yes |
| D. Change | Phase 5 | No (Siamese optional Nice) |
| E. Forecast baselines | Phase 6 | No |
| F. ConvLSTM | Phase 7 | Yes |
| G. Credibility pack | Phases 9–11 | Mix |

**Rule:** If NDVI city green % does not work, you are not ready for U-Net. If LULC looks wrong, do not start ConvLSTM.

---

## 7. Later credibility pack (MUST include — after core works)

These are **required for a strong viva** but belong in **later phases**, not Week 1.

| Item | Phase | Deliverable |
|---|---|---|
| **Ward priority score** | **9** | Ranked CSV + map; documented weights |
| **What-if scenarios** | **9** | BAU vs one intervention; Δ green % |
| **Forecast uncertainty bands** | **10** | Ensemble/MC/bootstrap bands + figure |
| **Live Streamlit Community Cloud demo** | **11** | Public URL; slider + CSV |

Do **not** bury these in “nice polish.” They are **Should** items with explicit phases after the Week-7 Must gate.

---

## 8. Eval metrics & report tables (viva numbers)

| Component | Metrics | File to produce |
|---|---|---|
| Segmentation | Per-class IoU, mean IoU, F1, OA, confusion matrix | `reports/tables/seg_metrics.csv` |
| Baselines | Same metrics for NDVI threshold + RF | same table, extra rows |
| Change | Precision, recall, kappa on ≥50 samples | `reports/tables/change_metrics.csv` |
| Forecast | OA, kappa; **ward green-% RMSE & MAE**; 3 models | `reports/tables/forecast_comparison.csv` |
| Uncertainty | Band width / coverage note vs held-out | `reports/tables/uncertainty_notes.md` |
| Impact | Pearson r, p, R² for LST–green and NO₂–green | `reports/tables/impact_correlations.csv` |
| Priority | Top-10 wards + score components | `reports/tables/priority_top10.csv` |
| Scenario | Δ city green %, Δ selected wards | `reports/tables/scenario_delta.csv` |
| Dashboard | Load time note; live URL | `docs/DEMO_SCRIPT.md` |

**Figures (minimum):** city green trend; LULC A vs B; change map; forecast vs actual; LST scatter; priority map; scenario before/after; uncertainty band chart; train curves.

---

## 9. Risks & recovery

| Risk | Recovery |
|---|---|
| Monsoon clouds / empty S2 composite | Post-monsoon window; stricter/looser cloud filter; `s2cloudless`; document year gaps |
| Label noise (WorldCover fringe) | Manual tile QC; report agreement; don’t hide errors |
| Colab GPU disconnect | Checkpoint every best IoU; Kaggle backup; smaller batches |
| ConvLSTM unstable | Hard gate: ship persistence + CA-Markov; document failure |
| 10 m misses tiny parks | Aggregate to wards; state limitation aloud |
| CRS / hectare errors | Always area in EPSG:32645; unit-test known polygon |
| Data leakage | Spatial tile hold-out; held-out **year** for forecast |
| Huge rasters | Windowed reads; COGs; don’t commit TIFFs to Git |
| GEE quota / export fail | Smaller AOI clip; fewer bands; retry; cache Drive |
| Dashboard slow / Cloud too large | Precompute everything; PNG/COG overlays; Drive for full rasters |
| Scope creep (GAN, alerts, 2nd city) | Nice only in Phase 12 if Must green |
| Ward attribute mismatch | Normalize to `ward_id` once in Phase 0 |

---

## 10. Handoff prompt for next AI agent

Copy-paste as the first message when starting work:

```text
You are building the EaseCare-unrelated FYP repo `green-cover-fyp` for Debayan Sarkar.

READ FIRST (do not invent conflicting scope):
- /cursor/stores/self/docs/agent-build-plan.md   ← THIS is the source of truth
- /cursor/stores/self/docs/concrete-finish-plan.md  (stack only; city superseded)
- /cursor/stores/self/docs/beginner-model-training-guide.md
- /cursor/stores/self/docs/green-cover-fyp-plan.md

LOCKED CONSTRAINTS:
- City: Kolkata (KMC), 141 wards — DO NOT switch to Bengaluru unless wards are unblockable; if so, write the blocker in docs/study_area.md
- Years: 2018–2024; season Oct 1–Feb 28; classes 0=vegetation,1=built-up,2=water,3=barren
- Stack: GEE + Sentinel-2 + WorldCover + PyTorch SMP U-Net ResNet34 + Persistence/CA-Markov/ConvLSTM + Streamlit; free only
- CRS: export EPSG:4326; area EPSG:32645
- Ward source: DataMeet Kolkata/kolkata.geojson (attr WARD → ward_id)
- No ease-care monorepo edits. No paid APIs.

YOU ARE BUILDING: Phase X only (replace X).
- Implement only that phase’s Agent steps + scripts listed in agent-build-plan.md
- Leave Human steps as checklists for Debayan (GEE auth, exports, Colab GPU, visual QC, Cloud deploy OAuth)
- Do not expand into later phases (especially priority/scenarios/uncertainty/Streamlit deploy before Phase 7 Must gate is done)
- Follow data contracts (file paths, class IDs, ward_id) exactly
- When Phase X Acceptance tests are ready, stop and report: files created, what Debayan must run next, and any Stop-if-blocked hit

Start by reading Phase X in agent-build-plan.md and listing the files you will create.
```

**Phase cheat-sheet for the blank above:**

| X | Title |
|---|---|
| 0 | Accounts, city lock, repo skeleton |
| 1 | First mosaic + NDVI |
| 2 | Multi-year indices + ward green % |
| 3 | Labels + tiles |
| 4 | U-Net + RF baseline |
| 5 | Multi-year LULC + change |
| 6 | Forecast baselines (persistence + CA-Markov) |
| 7 | ConvLSTM + hard gate |
| 8 | Impact (LST + pollution) |
| 9 | Ward priority score + what-if scenarios |
| 10 | Forecast uncertainty bands |
| 11 | Streamlit app + live Community Cloud demo |
| 12 | Polish, freeze, viva pack |

---

## Quick start (Debayan — this week)

1. Phase 0: GEE auth + download DataMeet wards + agent creates repo/config.  
2. Phase 1: one-year S2 export + NDVI.  
3. Follow beginner guide order: **NDVI → labels → U-Net**.  
4. Do not open Phase 9–11 until Phase 7 Must metrics exist.

---

*Supersedes city recommendation in `concrete-finish-plan.md`. Stack, Must/Should/Nice, and ML order remain aligned with the synopsis + companion docs. No ease-care code changes.*