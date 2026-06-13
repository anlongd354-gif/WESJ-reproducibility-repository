from __future__ import annotations

"""Shared configuration, raster I/O, grid checking, and serialization helpers.

Inputs: local path YAML, public parameter YAML, and raster arrays/files.
Parameters: NoData value, file patterns, and grid metadata.
Outputs: in-memory arrays or generic GeoTIFF/JSON products requested by the
calling analytical script.
Paper/SI: technical support for manuscript Sections 2.2.2-2.3 and Texts S6-S9;
this module does not implement an independent scientific method.
"""

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = REPOSITORY_ROOT / "config" / "paths_local.yaml"
DEFAULT_PARAMETERS = REPOSITORY_ROOT / "config" / "parameters.yaml"
EPS = 1e-12


def load_yaml(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_absolute():
        source = REPOSITORY_ROOT / source
    if not source.exists():
        raise FileNotFoundError(source)
    with source.open("r", encoding="utf-8") as handle:
        content = yaml.safe_load(handle)
    if not isinstance(content, dict):
        raise ValueError(f"YAML root must be a mapping: {source}")
    return content


def load_settings(
    paths_file: str | Path | None = None,
    parameters_file: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    local_paths = (
        Path(paths_file)
        if paths_file
        else Path(os.environ.get("WESJ_PATHS_CONFIG", DEFAULT_PATHS))
    )
    if not local_paths.exists():
        raise FileNotFoundError(
            "Private path configuration is missing. Copy "
            "config/paths_template.yaml to config/paths_local.yaml and edit "
            "only the local copy."
        )
    parameters = parameters_file or DEFAULT_PARAMETERS
    return load_yaml(local_paths), load_yaml(parameters)


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPOSITORY_ROOT / path


def format_path(pattern: str, **values: object) -> Path:
    return resolve_path(pattern.format(**values))


def years_from_paths(paths: dict[str, Any]) -> list[int]:
    years = paths.get("project", {}).get("years", [])
    if not years:
        raise ValueError("Set project.years in config/paths_local.yaml.")
    return [int(year) for year in years]


def read_raster(
    path: str | Path,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    source = resolve_path(path)
    with rasterio.open(source) as src:
        band = src.read(1, masked=True).astype("float64")
        data = np.asarray(band.filled(np.nan), dtype="float64")
        valid = ~np.ma.getmaskarray(band)
        valid &= np.isfinite(data)
        return data, valid, src.profile.copy()


def assert_same_grid(profiles: list[dict[str, Any]]) -> None:
    if not profiles:
        return
    first = profiles[0]
    for index, profile in enumerate(profiles[1:], start=2):
        for key in ("width", "height", "crs", "transform"):
            if profile[key] != first[key]:
                raise ValueError(
                    f"Raster grid mismatch at input {index}: {key} differs."
                )


def write_raster(
    path: str | Path,
    values: np.ndarray,
    profile: dict[str, Any],
    nodata: float = -9999.0,
) -> None:
    output = resolve_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    array = np.where(np.isfinite(values), values, nodata).astype("float32")
    metadata = profile.copy()
    metadata.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        nodata=nodata,
        compress="lzw",
        tiled=True,
        predictor=3,
        BIGTIFF="IF_SAFER",
    )
    with rasterio.open(output, "w", **metadata) as dst:
        dst.write(array, 1)
        dst.write_mask(np.where(np.isfinite(values), 255, 0).astype("uint8"))


def minmax_columns(values: np.ndarray) -> np.ndarray:
    result = np.zeros_like(values, dtype="float64")
    for column in range(values.shape[1]):
        data = values[:, column]
        low = float(np.min(data))
        high = float(np.max(data))
        result[:, column] = (
            1.0 if high - low <= EPS else (data - low) / (high - low)
        )
    return np.clip(result, 0.0, 1.0)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = resolve_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
