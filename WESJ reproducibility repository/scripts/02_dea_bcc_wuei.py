from __future__ import annotations

"""Calculate pixel-level WUEI with the original local DEA-BCC workflow.

Inputs: population density, water consumption, cropland ratio, and water
ecosystem service value rasters for each year.
Parameters: input orientation, VRS/BCC constraint, 11 x 11 neighborhood,
minimum 10 DMUs, 512-pixel tiles, five-pixel halo, and HiGHS solver.
Outputs: annual `wuei_{year}.tif` efficiency rasters.
Paper/SI: manuscript Section 2.2.3 and Table 1; water ecosystem service value
input preparation in Text S4.
"""

from contextlib import ExitStack
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window
from scipy.optimize import linprog

from common import (
    format_path,
    load_settings,
    resolve_path,
    years_from_paths,
)


def input_oriented_bcc_efficiency(
    inputs: np.ndarray,
    outputs: np.ndarray,
    target_index: int,
    epsilon: float,
) -> float:
    """Solve the input-oriented BCC model for one target DMU."""
    n_dmus, n_inputs = inputs.shape
    n_outputs = outputs.shape[1]
    x = np.maximum(inputs, 0.0) + epsilon
    y = np.maximum(outputs, 0.0) + epsilon
    x0 = x[target_index]
    y0 = y[target_index]

    # Variables: lambda_j, input slacks, output slacks, and theta.
    variable_count = n_dmus + n_inputs + n_outputs + 1
    theta_index = variable_count - 1
    objective = np.zeros(variable_count)
    objective[theta_index] = 1.0

    equalities = []
    targets = []
    for column in range(n_inputs):
        row = np.zeros(variable_count)
        row[:n_dmus] = x[:, column]
        row[n_dmus + column] = 1.0
        row[theta_index] = -x0[column]
        equalities.append(row)
        targets.append(0.0)
    for column in range(n_outputs):
        row = np.zeros(variable_count)
        row[:n_dmus] = y[:, column]
        row[n_dmus + n_inputs + column] = -1.0
        equalities.append(row)
        targets.append(y0[column])

    convexity = np.zeros(variable_count)
    convexity[:n_dmus] = 1.0
    equalities.append(convexity)
    targets.append(1.0)

    solution = linprog(
        objective,
        A_eq=np.vstack(equalities),
        b_eq=np.asarray(targets),
        bounds=[(0.0, None)] * (variable_count - 1) + [(0.0, 1.0)],
        method="highs",
    )
    if solution.success and np.isfinite(solution.x[theta_index]):
        return float(solution.x[theta_index])
    return np.nan


def windows_with_halo(
    width: int,
    height: int,
    tile_size: int,
    halo: int,
):
    """Yield an output tile and the same tile padded by a clipped halo."""
    for row in range(0, height, tile_size):
        tile_height = min(tile_size, height - row)
        for column in range(0, width, tile_size):
            tile_width = min(tile_size, width - column)
            inner = Window(column, row, tile_width, tile_height)
            padded = Window(
                max(0, column - halo),
                max(0, row - halo),
                min(width, column + tile_width + halo)
                - max(0, column - halo),
                min(height, row + tile_height + halo)
                - max(0, row - halo),
            )
            yield inner, padded


def aligned_vrt(source, template, resampling: Resampling):
    """Align a source to the cropland-ratio template without masking zero."""
    return WarpedVRT(
        source,
        crs=template.crs,
        transform=template.transform,
        width=template.width,
        height=template.height,
        resampling=resampling,
        src_nodata=None,
        dst_nodata=np.nan,
        dtype="float32",
    )


def calculate_year(
    population_path: Path,
    water_consumption_path: Path,
    cropland_ratio_path: Path,
    ecosystem_service_value_path: Path,
    output_path: Path,
    window_size: int,
    minimum_dmus: int,
    tile_size: int,
    epsilon: float,
) -> None:
    radius = window_size // 2
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with ExitStack() as stack:
        cropland = stack.enter_context(rasterio.open(cropland_ratio_path))
        population_source = stack.enter_context(rasterio.open(population_path))
        consumption_source = stack.enter_context(
            rasterio.open(water_consumption_path)
        )
        service_source = stack.enter_context(
            rasterio.open(ecosystem_service_value_path)
        )
        population = stack.enter_context(
            aligned_vrt(population_source, cropland, Resampling.bilinear)
        )
        consumption = stack.enter_context(
            aligned_vrt(consumption_source, cropland, Resampling.bilinear)
        )
        service = stack.enter_context(
            aligned_vrt(service_source, cropland, Resampling.bilinear)
        )

        profile = cropland.profile.copy()
        profile.update(
            driver="GTiff",
            dtype="float32",
            nodata=np.nan,
            count=1,
            compress="lzw",
            tiled=True,
            blockxsize=256,
            blockysize=256,
            BIGTIFF="IF_SAFER",
        )
        destination = stack.enter_context(
            rasterio.open(output_path, "w", **profile)
        )

        all_windows = list(
            windows_with_halo(
                cropland.width, cropland.height, tile_size, radius
            )
        )
        for tile_number, (inner, padded) in enumerate(all_windows, start=1):
            crop = cropland.read(
                1, window=padded, out_dtype="float32", masked=True
            ).filled(np.nan)
            pop = population.read(
                1, window=padded, out_dtype="float32", masked=True
            ).filled(np.nan)
            water = consumption.read(
                1, window=padded, out_dtype="float32", masked=True
            ).filled(np.nan)
            esv = service.read(
                1, window=padded, out_dtype="float32", masked=True
            ).filled(np.nan)

            inputs = np.dstack([pop, water, crop]).astype("float32")
            outputs = esv[..., None].astype("float32")
            valid = np.isfinite(inputs).all(axis=2)
            valid &= np.isfinite(outputs).all(axis=2)

            height, width, _ = inputs.shape
            efficiency = np.full((height, width), np.nan, dtype="float32")
            for row in range(height):
                row_min = max(0, row - radius)
                row_max = min(height, row + radius + 1)
                for column in np.flatnonzero(valid[row]):
                    col_min = max(0, column - radius)
                    col_max = min(width, column + radius + 1)
                    local_valid = valid[row_min:row_max, col_min:col_max]
                    if np.count_nonzero(local_valid) < minimum_dmus:
                        continue
                    local_inputs = inputs[
                        row_min:row_max, col_min:col_max
                    ][local_valid]
                    local_outputs = outputs[
                        row_min:row_max, col_min:col_max
                    ][local_valid]
                    positions = np.argwhere(local_valid)
                    target = np.flatnonzero(
                        (positions[:, 0] == row - row_min)
                        & (positions[:, 1] == column - col_min)
                    )
                    if target.size == 0:
                        continue
                    value = input_oriented_bcc_efficiency(
                        local_inputs,
                        local_outputs,
                        int(target[0]),
                        epsilon,
                    )
                    if np.isfinite(value):
                        efficiency[row, column] = value

            row_offset = int(inner.row_off - padded.row_off)
            column_offset = int(inner.col_off - padded.col_off)
            inner_values = efficiency[
                row_offset : row_offset + int(inner.height),
                column_offset : column_offset + int(inner.width),
            ]
            destination.write(inner_values, 1, window=inner)
            print(f"DEA tile completed: {tile_number}/{len(all_windows)}")


def main() -> None:
    paths, parameters = load_settings()
    settings = parameters["dea_bcc_wuei"]
    window_size = int(settings["neighborhood_window_size"])
    if window_size < 1 or window_size % 2 == 0:
        raise ValueError("DEA neighborhood_window_size must be odd.")
    raster_patterns = paths["inputs"]["rasters"]

    for year in years_from_paths(paths):
        calculate_year(
            format_path(raster_patterns["population_density"], year=year),
            format_path(raster_patterns["water_consumption"], year=year),
            format_path(raster_patterns["cropland_ratio"], year=year),
            format_path(raster_patterns["ecosystem_service_value"], year=year),
            resolve_path(
                paths["outputs"]["wuei_pattern"].format(year=year)
            ),
            window_size,
            int(settings["minimum_dmus"]),
            int(settings["tile_size"]),
            float(settings["epsilon"]),
        )
        print(f"{year}: WUEI written.")


if __name__ == "__main__":
    main()
