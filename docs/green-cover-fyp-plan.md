# Green Cover FYP — Architecture & Module Detail

**Student:** Debayan Sarkar  
**Project:** Satellite-Based Green Cover Monitoring and Forecasting System  
**Role:** Architecture & module companion to [agent-build-plan.md](./agent-build-plan.md)  
**City:** **Kolkata Municipal Corporation (KMC), 141 wards** (Bengaluru drafts superseded — see agent-build-plan §2.1)  
**Years:** 2018–2024 · Season: Oct 1–Feb 28 · Classes: vegetation / built-up / water / barren  

**Related:** [green-cover-docs-index.md](./green-cover-docs-index.md) · [concrete-finish-plan.md](./concrete-finish-plan.md) · [beginner-model-training-guide.md](./beginner-model-training-guide.md)

---

## 1. System overview

```text
GEE (S2 / LST / S5P / WorldCover)
        │
        ▼
   raw GeoTIFFs + ward GeoJSON
        │
        ├──► indices (NDVI…) ──► ward green % (threshold path)
        │
        ├──► labels remap + tiles ──► RF + U-Net ──► yearly LULC
        │                                              │
        │                              change (gain/loss/unchanged)
        │                                              │
        │                    Persistence / CA-Markov / ConvLSTM
        │                                              │
        ├──► impact (LST, NO₂ vs green)
        │
        └──► decision (priority score, scenarios, uncertainty)
                       │
                       ▼
              Streamlit (precomputed) → Community Cloud
```

**Design principle:** every dashboard layer is a **precomputed** file under `data/processed/`. The live app never calls GEE.

---

## 2. Study area (locked)

| Field | Value |
|---|---|
| AOI | Kolkata Municipal Corporation |
| Wards | 141 polygons (DataMeet primary) |
| Bbox (approx) | lon 88.24–88.46, lat 22.45–22.63 |
| Map center | (22.54, 88.35) |
| Export CRS | EPSG:4326 |
| Area CRS | EPSG:32645 (UTM 45N) |
| Optical | Sentinel-2 10 m |

Ward source:  
`https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Kolkata/kolkata.geojson`  
Normalize `WARD` → `ward_id` on first ingest. Document URL/date/licence in `data/raw/boundaries/SOURCE.md`.

---

## 3. Module map (`src/`)

| Package | Responsibility | Key scripts (per agent-build-plan) |
|---|---|---|
| `gee/` | Earth Engine exports + ward normalize | `normalize_wards.py`, `export_s2_one_year.py`, `export_s2_yearly.py`, `export_labels.py`, `export_lst.py`, `export_s5p.py` |
| `preprocess/` | Grid align, 256 tiles, nodata skip | `align.py`, `tile.py` |
| `indices/` | NDVI/EVI/NDBI/NDWI/NDMI; ward green | `compute.py`, `week1_ndvi.py`, `ward_green.py` |
| `classify/` | Remap labels; RF; U-Net; infer LULC | `remap_labels.py`, `train_rf.py`, `train_unet.py`, `infer_lulc.py` |
| `change/` | Gain/loss/unchanged; ward rank | `detect.py`, `ward_rank.py` |
| `forecast/` | Persistence, CA-Markov, ConvLSTM, unc. | `persistence.py`, `ca_markov.py`, `convlstm.py`, `uncertainty.py` |
| `impact/` | Green vs LST / NO₂ correlations | `correlate.py` |
| `decision/` | Priority score + scenarios | `priority.py`, `scenarios.py` |
| `dashboard/` | Streamlit UI | `app.py` |
| `api/` | Optional thin FastAPI | `main.py` |

Configs live in `configs/` (`city_aoi.yaml`, `class_map.yaml`, `priority_weights.yaml`). Data contracts (paths, dtypes, class IDs) are locked in [agent-build-plan.md](./agent-build-plan.md) §4 — do not rename casually.

---

## 4. Data flow by stage

### 4.1 Optical + indices (Phases 1–2)
1. Seasonal median S2 composite → `data/raw/s2/s2_median_{year}.tif` (6 bands).  
2. NDVI (and optional other indices) → `data/processed/ndvi/`.  
3. Threshold green (`ndvi_green_threshold`, default 0.35) → city + ward `green_pct` in `ward_year`.  
4. Areas always in EPSG:32645.

### 4.2 Labels + tiles (Phase 3)
1. WorldCover clip → remap to {0,1,2,3} via `class_map.yaml`.  
2. Align label grid to S2 transform.  
3. Cut 256×256 tiles; spatial train/val (~80/20); `manifest.csv`.  
4. Human QC: park, dense core, Hooghly water.

### 4.3 Segmentation (Phase 4)
1. RF baseline on same val tiles.  
2. U-Net ResNet34 (SMP), Dice+Focal, Colab GPU → `models/unet_best.pt`.  
3. Windowed inference → `lulc_{year}.tif`.  
4. Metrics: IoU / F1 / OA vs NDVI threshold vs RF vs U-Net.

Training order for beginners: [beginner-model-training-guide.md](./beginner-model-training-guide.md).

### 4.4 Change (Phase 5)
- Veg → built = **loss**; non-veg → veg = **gain**; else unchanged.  
- Outputs: `change_{y0}_{y1}.tif`, ward loss ranking, ≥50 verified samples.

### 4.5 Forecast (Phases 6–7, 10)
| Model | Role |
|---|---|
| Persistence | Copy last observed LULC / green as forecast |
| CA-Markov | Transition matrix + suitability + CA allocation |
| ConvLSTM | Spatiotemporal DL attempt (may fail; document) |

Held-out year default **2024**. Primary demo model chosen at Phase 7 hard gate. Uncertainty (Phase 10): ensemble / MC dropout / bootstrap transitions.

### 4.6 Impact (Phase 8)
- Landsat LST (°C) and S5P NO₂ seasonal means → ward aggregates.  
- Pearson r, p (and R²) vs green % — ward level, not park scale.

### 4.7 Decision support (Phase 9)
**Priority score (document weights):**  
`score = w1*(1-green) + w2*lst_norm + w3*built + w4*pop_density` (0–1 normalized; drop pop if no grid).

**Scenarios:** BAU vs one intervention (protect polygon or plant barren→veg); recompute lightweight forecast; report Δ green %.

### 4.8 Product (Phases 11–12)
Streamlit: Folium map, year slider, layers (NDVI/LULC/change/forecast/unc/priority), ward charts, scenario toggle, CSV export. Deploy to Streamlit Community Cloud. Tag `v1.0-demo`.

---

## 5. Class map (4 classes)

| ID | Name | WorldCover grouping (detail in `class_map.yaml`) |
|---|---|---|
| 0 | vegetation | tree, shrub, grass, crop, mangrove, moss/lichen (+ wetland if green-focused) |
| 1 | built-up | built-up |
| 2 | water | permanent water (+ snow/ice if any) |
| 3 | barren | bare / sparse |

LULC nodata = **255**.

---

## 6. Repo tree (summary)

Full tree is in [agent-build-plan.md](./agent-build-plan.md) §3. Top level:

```text
green-cover-fyp/
├── configs/          # city_aoi, class_map, priority_weights
├── data/raw|interim|processed/
├── src/{gee,preprocess,indices,classify,change,forecast,impact,decision,api,dashboard}/
├── notebooks/        # week1 NDVI, U-Net Colab, ConvLSTM Colab
├── models/           # gitignored checkpoints
├── reports/{figures,tables}/
├── docs/             # study_area, DEMO_SCRIPT, metrics_log
└── tests/
```

New repo/folder — **not** inside ease-care.

---

## 7. Report / viva chapter outline (§8 companion)

Use this outline when filling Phase 12 report/PPT (agent fills from results; Debayan owns narrative):

1. **Introduction** — problem, Kolkata green loss, objectives  
2. **Study area & data** — KMC 141 wards, S2/LST/S5P/WorldCover, CRS  
3. **Methodology** — indices → labels → U-Net → change → forecast → impact → decision  
4. **Implementation** — free stack, Colab, Streamlit Cloud  
5. **Results** — tables in `reports/tables/` (seg, change, forecast, impact, priority, scenario)  
6. **Discussion** — 10 m limits, label noise, ConvLSTM outcome honesty  
7. **Conclusion & future work** — Nice items only if Must green  
8. **Demo** — live URL + DEMO_SCRIPT (≤10 min)

Minimum figures: city green trend; LULC A vs B; change map; forecast vs actual; LST scatter; priority map; scenario before/after; uncertainty band; train curves.

---

## 8. Risks (architecture lens)

| Risk | Architectural recovery |
|---|---|
| Cloud / empty composites | Seasonal window; document year gaps; never invent rasters |
| Label noise | Remap + tile QC; report agreement |
| CRS hectare bugs | Single area CRS 32645; unit-test polygon |
| Data leakage | Spatial tile hold-out; held-out **year** for forecast |
| Huge rasters | Windowed IO; COGs; Drive for full; PNG overlays on Cloud |
| Scope creep | Nice only after Must; credibility pack after Phase 7 |

Full risk table: [agent-build-plan.md](./agent-build-plan.md) §9.

---

## 9. How to use this doc with agents

1. Read [agent-build-plan.md](./agent-build-plan.md) for the phase you are on (Human/Agent/Acceptance/Stop-if-blocked).  
2. Use **this** file for module boundaries and data-flow intent.  
3. Use [beginner-model-training-guide.md](./beginner-model-training-guide.md) when entering Phase 3–4.  
4. Use [concrete-finish-plan.md](./concrete-finish-plan.md) for stack + week pacing.  
5. Paste the handoff prompt in agent-build-plan §10 with `Phase X` filled in.

---

*Aligned with locked agent-build-plan (Kolkata KMC). Do not reintroduce Bengaluru as the primary AOI.*
