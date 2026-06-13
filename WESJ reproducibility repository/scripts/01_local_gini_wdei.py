from __future__ import annotations

"""Calculate pixel-level Local Gini values used as the WDEI component.

Inputs: annual ArcGIS-derived `wrli_{year}.tif` rasters.
Parameters: moving-window size and minimum valid-pixel count.
Outputs: annual `wdei_{year}.tif` Local Gini rasters.
Paper/SI: manuscript Section 2.2.2, item (2); window and validity sensitivity
in Text S6 and Table S1.
"""

import numpy as np
from scipy import ndimage

from common import (
    format_path,
    load_settings,
    read_raster,
    write_raster,
    years_from_paths,
)


def gini_coefficient(window: np.ndarray, minimum_valid: int) -> np.float32:
    values = window[np.isfinite(window)]
    values = values[values >= 0].astype("float64")
    n = values.size
    if n < minimum_valid:
        return np.float32(np.nan)
    total = float(values.sum())
    if total <= 0.0:
        return np.float32(0.0 if np.all(values == 0.0) else np.nan)
    ordered = np.sort(values)
    ranks = np.arange(1, n + 1, dtype="float64")
    gini = 2.0 * np.sum(ranks * ordered) / (n * total) - (n + 1.0) / n
    return np.float32(np.clip(gini, 0.0, 1.0))


def calculate_local_gini(
    wrli: np.ndarray,
    valid: np.ndarray,
    window_size: int,
    minimum_valid: int,
) -> np.ndarray:
    if window_size < 1 or window_size % 2 == 0:
        raise ValueError("Local Gini window_size must be a positive odd integer.")
    source = np.where(valid & (wrli >= 0), wrli, np.nan)
    result = ndimage.generic_filter(
        source,
        function=lambda values: gini_coefficient(values, minimum_valid),
        size=window_size,
        mode="constant",
        cval=np.nan,
    ).astype("float64")
    result[~valid] = np.nan
    return result


def main() -> None:
    paths, parameters = load_settings()
    settings = parameters["local_gini_wdei"]
    window_size = int(settings["baseline_window_size"])
    minimum_valid = int(settings["baseline_minimum_valid_pixels"])

    for year in years_from_paths(paths):
        source = format_path(
            paths["inputs"]["derived_rasters"]["wrli"], year=year
        )
        wrli, valid, profile = read_raster(source)
        wdei = calculate_local_gini(
            wrli, valid, window_size, minimum_valid
        )
        output = format_path(paths["outputs"]["wdei_pattern"], year=year)
        write_raster(output, wdei, profile)
        print(
            f"{year}: WDEI written with {window_size}x{window_size} window "
            f"and minimum {minimum_valid} valid pixels."
        )


if __name__ == "__main__":
    main()
