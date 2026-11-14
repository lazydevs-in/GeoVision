"""Synthetic fixture for ward normalize (WARD→ward_id, dissolve, bbox)."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

from src.gee.normalize_wards import normalize_wards

pytest.importorskip("geopandas")


def test_normalize_wards_renames_and_dissolves(tmp_path: Path) -> None:
    gdf = gpd.GeoDataFrame(
        {"WARD": [1, 2]},
        geometry=[box(88.30, 22.50, 88.31, 22.51), box(88.32, 22.52, 88.33, 22.53)],
        crs="EPSG:4326",
    )
    wards_path = tmp_path / "wards.geojson"
    aoi_path = tmp_path / "aoi.geojson"
    gdf.to_file(wards_path, driver="GeoJSON")

    cfg = {
        "n_wards": 2,
        "bbox": [88.30, 22.50, 88.33, 22.53],
    }
    out = normalize_wards(wards_path=wards_path, aoi_path=aoi_path, config=cfg)

    assert "ward_id" in out.columns
    assert "WARD" not in out.columns
    assert len(out) == 2
    assert aoi_path.exists()
    aoi = gpd.read_file(aoi_path)
    assert len(aoi) == 1
