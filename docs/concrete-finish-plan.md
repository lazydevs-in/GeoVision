# Concrete Finish Plan — Green Cover FYP

**Student:** Debayan Sarkar  
**Role:** Locked free stack + week calendar companion to the definitive [agent-build-plan.md](./agent-build-plan.md)  
**Plan date:** 2026-11-13  
**Status:** LOCKED stack; city superseded (see below)

**City supersession:** Early drafts of this companion used **Bengaluru (BBMP)** as a placeholder AOI. That recommendation is **superseded**. The locked city is **Kolkata Municipal Corporation (KMC), 141 wards**, per [agent-build-plan.md](./agent-build-plan.md) §2.1. Stack, week order, Must/Should/Nice, and ML path are unchanged; only AOI + ward polygons differ. Always treat `agent-build-plan.md` as the source of truth for city.

**Related docs:** [green-cover-docs-index.md](./green-cover-docs-index.md) · [green-cover-fyp-plan.md](./green-cover-fyp-plan.md) · [beginner-model-training-guide.md](./beginner-model-training-guide.md)

---

## 1. Locked free stack (do not swap mid-FYP)

| Layer | Choice | Why / notes |
|---|---|---|
| Imagery access | **Google Earth Engine** + `earthengine-api` / `geemap` | Free Sentinel-2, Landsat LST, S5P, WorldCover |
| Optical | Sentinel-2 SR Harmonized, **10 m**, bands B2–B4,B8,B11,B12 | Post-monsoon median Oct 1–Feb 28 |
| Labels | ESA WorldCover v200 (primary); Dynamic World second opinion | Remap → 4 classes |
| Boundaries | DataMeet Kolkata wards GeoJSON (141) | `WARD` → `ward_id`; area in EPSG:32645 |
| Geo stack | rasterio, GeoPandas, NumPy, scikit-learn | Align, tiles, zonal stats, RF |
| Segmentation | PyTorch + `segmentation_models_pytorch` **U-Net ResNet34** | Colab T4 / Kaggle GPU |
| Forecast | **Persistence + CA-Markov + ConvLSTM** (all three) | Hard gate at Phase 7 |
| Dashboard | **Streamlit** + Folium + Plotly | Precomputed files only |
| Live demo | **Streamlit Community Cloud** | Public URL for viva |
| Optional API | Thin FastAPI reading `data/processed/` | After dashboard works |
| Compute | Google Colab (T4); Kaggle backup | No paid GPU required |
| Hosting of heavy rasters | Google Drive / local; **do not git-commit TIFFs** | COG / PNG overlays for Cloud |

**Hard rules**
- Free stack only — no paid imagery, no paid APIs for core pipeline.
- No ease-care / monorepo edits.
- Agents ship code/configs/checklists; Debayan owns Google login, GEE export, Colab GPU, visual QC, Cloud OAuth.

---

## 2. Must / Should / Nice (aligned with agent-build-plan)

| Priority | What | When |
|---|---|---|
| **Must** | Mapping, U-Net + RF, change, 3-model forecast comparison, core metrics | Through **Phase 7** |
| **Should (credibility pack)** | LST + pollution; ward priority; what-if scenarios; uncertainty bands; live Streamlit Cloud | Phases **8–11** |
| **Nice** | GAN, alerts, planting recommender, carbon, rich API, second city | Phase **12** only if Must green |

**Gate:** Do not open Phases 9–11 until Phase 7 Must metrics exist.

---

## 3. Week calendar (≈12 weeks ≈ Phases 0–12)

Use one phase per week unless blocked. Finish that phase’s Acceptance tests before starting the next. Full Inputs/Outputs/Human/Agent/Stop-if-blocked live in [agent-build-plan.md](./agent-build-plan.md) §5.

| Week | Phase | Focus | Human owns | Agent owns | Exit signal |
|---|---|---|---|---|---|
| 0 / start | **0** | Accounts, city lock, repo | GEE auth; download DataMeet wards; QGIS count 141 | Repo tree, `city_aoi.yaml`, normalize wards | GEE OK + wards + AOI on disk |
| 1 | **1** | First mosaic + NDVI | Run one-year export; visual true-color | Export scripts, NDVI compute, week1 figure | ≥1 S2 + NDVI GeoTIFF |
| 2 | **2** | Multi-year indices + ward green % | Finish yearly downloads; spot clouds | Batch NDVI; ward zonal CSV; trend chart | ≥6 years `green_pct` |
| 3 | **3** | Labels + tiles | Export WorldCover; QC park/core/water | Remap, align, tile 256, manifest | ≥200 train / ≥40 val |
| 4 | **4** | U-Net + RF | Colab GPU train; trust maps | Notebook, RF, infer LULC, metrics table | `unet_best.pt` + citywide LULC |
| 5 | **5** | Multi-year LULC + change | Infer years; ≥50 change samples | Change detect + ward loss rank | Change map + top-10 |
| 6 | **6** | Forecast baselines | Visual forecast vs actual | Persistence + CA-Markov + RMSE/MAE | 2-model table |
| 7 | **7** | ConvLSTM + **hard gate** | Train / decide primary model | ConvLSTM + 3-row comparison | Must gate met |
| 8 | **8** | Impact LST + NO₂ | GEE exports; unit sanity | Correlate + scatters | r, p tables |
| 9 | **9** | Priority + scenarios | Draw one scenario polygon | Priority score + BAU vs intervene | Top-10 + Δ green % |
| 10 | **10** | Uncertainty bands | Approve legend wording | Ensemble / MC / bootstrap | Band chart |
| 11 | **11** | Streamlit + Cloud | GitHub push; Cloud deploy OAuth | App (no live GEE); DEMO_SCRIPT | **Live public URL** |
| 12 | **12** | Polish / viva | Dry run + backup video | Report/PPT outlines; tag `v1.0-demo` | Checklist 100% |

**If behind:** finish Must through Phase 7 first. Drop Nice entirely. Credibility pack (9–11) can compress but should not skip the live URL if viva needs a clickable demo.

---

## 4. City & data locks (quick reference)

| Item | Locked value |
|---|---|
| City | **Kolkata (KMC)** — *not Bengaluru* |
| Wards | 141; DataMeet `kolkata.geojson` |
| Years | 2018–2024 |
| Season | Oct 1 → Feb 28 |
| Classes | 0 veg, 1 built, 2 water, 3 barren |
| CRS export | EPSG:4326 |
| CRS area | EPSG:32645 (UTM 45N) |
| Tile | 256×256 |
| Held-out forecast year | 2024 (default) |

Canonical ward URL:  
`https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Kolkata/kolkata.geojson`

---

## 5. Demo finish checklist (same as agent-build-plan success)

- [ ] AOI: Kolkata KMC, 141 wards, 2018–2024  
- [ ] City green-% trend (≥6 years)  
- [ ] LULC A vs B (4 classes)  
- [ ] Change map + top-5 green-loss wards  
- [ ] Forecast vs held-out + 3-model metrics + uncertainty bands  
- [ ] LST–green scatter (r, p)  
- [ ] NO₂/aerosol vs green (ward)  
- [ ] Priority wards + one scenario Δ green %  
- [ ] Live Streamlit Community Cloud URL  
- [ ] Limitations said aloud (10 m, open labels, no legal enforcement)

---

## 6. What this companion is / is not

| Is | Is not |
|---|---|
| Locked free stack + week calendar | Full phase scripts / Acceptance tests (see agent-build-plan) |
| Reminder that Bengaluru drafts are obsolete | A second city decision document |
| Pointer into credibility pack timing | Architecture deep-dive (see [green-cover-fyp-plan.md](./green-cover-fyp-plan.md)) |
| Calendar companion for beginners | Training recipe (see [beginner-model-training-guide.md](./beginner-model-training-guide.md)) |

---

*City recommendation in older Bengaluru-era notes is superseded by [agent-build-plan.md](./agent-build-plan.md). Stack and calendar remain aligned.*
