from __future__ import annotations

"""Evaluate WSI sensitivity to alpha and water-demand composition.

Inputs: agricultural, domestic, and ecological water use plus carrying
capacity rasters.
Parameters: configured alpha values and agricultural-only versus total-demand
scenarios; the baseline simplified WSI omits the uniform phi coefficient.
Outputs: scenario WSI rasters and `wsi_sensitivity_summary.csv`.
Paper/SI: manuscript Section 2.2.1 and Text S5.
"""

import csv

import numpy as np

from common import (
    assert_same_grid,
    format_path,
    load_settings,
    read_raster,
    resolve_path,
    write_raster,
    years_from_paths,
)


def main() -> None:
    paths, parameters = load_settings()
    settings = parameters["wsi_sensitivity"]
    raster_patterns = paths["inputs"]["rasters"]
    output_dir = resolve_path(paths["outputs"]["wsi_sensitivity_directory"])
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for year in years_from_paths(paths):
        names = [
            "agricultural_water_use",
            "domestic_water_use",
            "ecological_water_use",
            "water_carrying_capacity",
        ]
        loaded = [
            read_raster(format_path(raster_patterns[name], year=year))
            for name in names
        ]
        assert_same_grid([item[2] for item in loaded])
        arrays = {name: loaded[index][0] for index, name in enumerate(names)}
        masks = {name: loaded[index][1] for index, name in enumerate(names)}

        for scenario in settings["water_use_scenarios"]:
            demand = (
                float(scenario["agricultural"])
                * arrays["agricultural_water_use"]
                + float(scenario["domestic"])
                * arrays["domestic_water_use"]
                + float(scenario["ecological"])
                * arrays["ecological_water_use"]
            )
            valid = masks["water_carrying_capacity"].copy()
            valid &= arrays["water_carrying_capacity"] > 0
            for component, multiplier in (
                ("agricultural_water_use", scenario["agricultural"]),
                ("domestic_water_use", scenario["domestic"]),
                ("ecological_water_use", scenario["ecological"]),
            ):
                if float(multiplier) != 0.0:
                    valid &= masks[component] & (arrays[component] >= 0)

            for alpha in settings["alpha_values"]:
                alpha = float(alpha)
                if not 0.0 <= alpha < 1.0:
                    raise ValueError(f"Invalid alpha: {alpha}")
                wsi = np.full(demand.shape, np.nan, dtype="float64")
                wsi[valid] = demand[valid] / (
                    (1.0 - alpha)
                    * arrays["water_carrying_capacity"][valid]
                )
                filename = (
                    f"wsi_{scenario['name']}_alpha_{alpha:.2f}_{year}.tif"
                )
                write_raster(output_dir / filename, wsi, loaded[0][2])
                values = wsi[np.isfinite(wsi)]
                rows.append(
                    {
                        "year": year,
                        "scenario": scenario["name"],
                        "alpha": alpha,
                        "valid_pixels": int(values.size),
                        "mean": float(np.mean(values)),
                        "median": float(np.median(values)),
                        "minimum": float(np.min(values)),
                        "maximum": float(np.max(values)),
                    }
                )

    with (output_dir / "wsi_sensitivity_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(output_dir)


if __name__ == "__main__":
    main()
