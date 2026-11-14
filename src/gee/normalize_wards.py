"""Normalize DataMeet wards: WARD→ward_id, dissolve AOI, bbox check."""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import yaml

ROOT = Path(__file__).resolve().parents[2]
WARDS_PATH = ROOT / "data" / "raw" / "boundaries" / "wards.geojson"
AOI_PATH = ROOT / "data" / "raw" / "boundaries" / "aoi.geojson"
CONFIG_PATH = ROOT / "configs" / "city_aoi.yaml"
# Allow small float drift vs published rough bbox (plan §2.1).
BBOX_TOL = 0.05


def load_config(path: Path = CONFIG_PATH) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_wards(
    wards_path: Path = WARDS_PATH,
    aoi_path: Path = AOI_PATH,
    config: dict | None = None,
) -> gpd.GeoDataFrame:
    cfg = config if config is not None else load_config()
    gdf = gpd.read_file(wards_path)
    if "WARD" in gdf.columns:
        gdf = gdf.rename(columns={"WARD": "ward_id"})
    if "ward_id" not in gdf.columns:
        raise ValueError("wards file missing WARD / ward_id")
    if gdf["ward_id"].nunique() != len(gdf):
        raise ValueError("ward_id values are not unique")
    expected_n = int(cfg.get("n_wards", 141))
    if len(gdf) != expected_n:
        raise ValueError(f"expected {expected_n} wards, got {len(gdf)}")

    gdf = gdf.to_crs("EPSG:4326")
    aoi_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(wards_path, driver="GeoJSON")

    aoi = gdf[["geometry"]].dissolve().reset_index(drop=True)
    aoi.to_file(aoi_path, driver="GeoJSON")

    minx, miny, maxx, maxy = gdf.total_bounds
    lon_min, lat_min, lon_max, lat_max = cfg["bbox"]
    if not (
        abs(minx - lon_min) <= BBOX_TOL
        and abs(miny - lat_min) <= BBOX_TOL
        and abs(maxx - lon_max) <= BBOX_TOL
        and abs(maxy - lat_max) <= BBOX_TOL
    ):
        raise ValueError(
            f"ward bbox {[minx, miny, maxx, maxy]} outside tolerance "
            f"of config bbox {cfg['bbox']} (tol={BBOX_TOL})"
        )
    print(f"OK: {len(gdf)} wards → {wards_path}")
    print(f"OK: AOI → {aoi_path}")
    print(f"OK: bbox check vs {cfg['bbox']}")
    return gdf


def main() -> int:
    normalize_wards()
    return 0


if __name__ == "__main__":
    sys.exit(main())
