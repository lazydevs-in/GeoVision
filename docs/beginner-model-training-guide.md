# Beginner Model Training Guide — NDVI → Labels → U-Net

**Student:** Debayan Sarkar  
**Role:** Ordered training guide for Phases 1–4 (and the gate into forecast)  
**City / data locks:** Kolkata KMC · 2018–2024 · Sentinel-2 10 m · 4 classes · tile 256  
**Source of truth:** [agent-build-plan.md](./agent-build-plan.md)  
**Related:** [green-cover-docs-index.md](./green-cover-docs-index.md) · [concrete-finish-plan.md](./concrete-finish-plan.md) · [green-cover-fyp-plan.md](./green-cover-fyp-plan.md)

---

## Why this order is mandatory

```text
NDVI threshold green %
    → WorldCover labels (4 classes) + tiles
        → RF baseline + U-Net (ResNet34)
            → Multi-year LULC → change → forecasts…
```

| If this fails… | Do not start… |
|---|---|
| City NDVI / green % | Labels or U-Net |
| Label–image alignment / QC | Any training |
| U-Net / RF LULC looks wrong | Change or ConvLSTM |

Deep learning is **step C**, not step A. Credibility pack (priority / scenarios / uncertainty / Streamlit Cloud) waits until Phase 7 Must metrics exist.

---

## Stage A — NDVI first (Phases 1–2)

### Goal
Prove exports + math work with **zero** neural nets.

### What you do
1. Export one seasonal S2 median for Kolkata AOI (`s2_median_{year}.tif`, 6 bands).  
2. Compute NDVI: `(B8 - B4) / (B8 + B4)` → `ndvi_{year}.tif`.  
3. Threshold (config `ndvi_green_threshold`, default **0.35**) → city green fraction.  
4. Repeat for ≥6 years; zonal stats per ward in **EPSG:32645**.  
5. Save `reports/figures/week1_ndvi.png` and city trend chart.

### Accept before leaving A
- [ ] GeoTIFF opens; NDVI roughly in [−1, 1]  
- [ ] Unit test for NDVI formula passes  
- [ ] ≥6 years of ward `green_pct` (or documented gaps)  
- [ ] Areas not computed in raw degrees  

### Common pitfalls
- Empty composite → loosen cloud % or confirm Oct–Feb window.  
- Wrong band order → locked order B2,B3,B4,B8,B11,B12.  
- Hectare nonsense → reproject for area to UTM 45N (32645).

---

## Stage B — Labels + tiles (Phase 3)

### Goal
Build a **spatially honest** dataset: images + 4-class masks.

### Class IDs (locked)

| ID | Name |
|---|---|
| 0 | vegetation |
| 1 | built-up |
| 2 | water |
| 3 | barren |

### What you do
1. Export ESA WorldCover for AOI; remap with `configs/class_map.yaml` → `{0,1,2,3}`.  
2. Align label raster to the S2 grid (same transform / size).  
3. Cut **256×256** tiles; skip mostly-nodata chips.  
4. Spatial train/val split (~80/20) — **not** random pixels from the same chip.  
5. Write `data/interim/tiles/manifest.csv`.  
6. **Human visual QC** in QGIS: park (veg), dense core (built), Hooghly (water). Fix egregious errors into `labels_verified/` if needed.

### Accept before leaving B
- [ ] Masks only contain {0,1,2,3}  
- [ ] ≥200 train + ≥40 val tiles; paths resolve  
- [ ] Side-by-side RGB vs mask for 3 sites  

### Stop
If image and mask are misaligned → **fix CRS/transform**. Do **not** open Colab for U-Net.

---

## Stage C — RF baseline + U-Net (Phase 4)

### Goal
A defensible segmentation story: U-Net on Colab, compared to RF and NDVI threshold.

### Random Forest (do this)
- Features: reflectance bands (± simple indices) on the **same val tiles**.  
- Metrics: IoU / F1 / OA so U-Net has a classical baseline.  
- Script target: `src/classify/train_rf.py`.

### U-Net setup (locked defaults)

| Item | Choice |
|---|---|
| Library | PyTorch + `segmentation_models_pytorch` |
| Architecture | **U-Net**, encoder **ResNet34** (ImageNet weights OK) |
| Input | 6-band tile `(6, 256, 256)` — adapt first conv if needed |
| Loss | Dice + Focal (class imbalance friendly) |
| Metric | Mean IoU (+ per-class IoU) |
| Hardware | Colab T4; checkpoint `models/unet_best.pt` |
| Backup | Kaggle GPU, same notebook |

### Colab checklist (Human)
1. Upload tiles zip / mount Drive.  
2. Runtime → GPU.  
3. Run `notebooks/train_unet_colab.ipynb`.  
4. Confirm best checkpoint saves on improved `val_iou`.  
5. **Trust maps:** inspect 5–10 val predictions before celebrating numbers.

### Inference
- Windowed / tiled inference over full AOI → `data/processed/lulc/lulc_{year}.tif` (uint8, nodata=255).  
- Script target: `src/classify/infer_lulc.py`.

### Accept before leaving C
- [ ] `unet_best.pt` with logged `val_iou`  
- [ ] `reports/tables/seg_metrics.csv` (NDVI threshold + RF + U-Net rows)  
- [ ] Citywide LULC opens in QGIS  
- [ ] U-Net ≥ RF on mean IoU **or** honest write-up why not  

### Debugging “all one class”
1. Re-check label IDs and class histogram.  
2. Class weights / Focal γ.  
3. Lower LR; confirm augmentations aren’t wrecking masks.  
4. Verify train tiles aren’t empty / single-class only.  
5. See agent-build-plan Phase 4 Stop-if-blocked.

---

## After Stage C (do not skip ahead)

| Next | Phase | Notes |
|---|---|---|
| Multi-year LULC + change | 5 | Need `unet_best.pt` + all yearly S2 |
| Persistence + CA-Markov | 6 | Classical forecast baselines |
| ConvLSTM + hard gate | 7 | May fail; still Must-complete comparison |
| Impact / credibility / Streamlit | 8–11 | **After** Phase 7 gate |

Forecast DL (ConvLSTM) is a **later** notebook (`train_convlstm_colab.ipynb`). Do not start it because U-Net “felt exciting.”

---

## Metrics you must log (viva)

| Table | Contents |
|---|---|
| `reports/tables/seg_metrics.csv` | Per-class IoU, mIoU, F1, OA, confusion; rows for NDVI / RF / U-Net |
| Train curves | Loss + val IoU figure under `reports/figures/` |
| `docs/metrics_log.md` | Dates, LR, batch size, best IoU, notes |

Full metrics matrix: [agent-build-plan.md](./agent-build-plan.md) §8.

---

## Minimal commands mental model

```text
# A — after GEE download
python -m src.indices.week1_ndvi          # one year proof
python -m src.indices.ward_green          # multi-year ward CSV

# B
python -m src.classify.remap_labels
python -m src.preprocess.align
python -m src.preprocess.tile

# C
# → train_unet_colab.ipynb on GPU
python -m src.classify.train_rf
python -m src.classify.infer_lulc --year 2023
```

Exact CLI flags live in the repo once Phase agents implement scripts; paths and contracts must match agent-build-plan §4.

---

## One-page mantra

1. **NDVI works** → then labels.  
2. **Labels QC + alignment** → then RF + U-Net.  
3. **LULC looks right** → then change / forecast.  
4. **Phase 7 Must metrics** → then priority / scenarios / uncertainty / Cloud demo.

Kolkata stays locked. Free stack only. No ease-care edits.
