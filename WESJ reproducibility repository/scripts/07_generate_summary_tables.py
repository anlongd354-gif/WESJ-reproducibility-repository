from __future__ import annotations

"""Merge ArcGIS Zonal Statistics exports into county-year summary tables.

Inputs: `zonal_{variable}_{year}.csv` files with unit ID, MEAN, and optional
COUNT fields.
Parameters: stable zone ID and the expected filename convention.
Outputs: `county_year_metrics.csv` and annual descriptive statistics.
Paper/SI: county-level aggregation in manuscript Sections 2.1-2.3; Texts
S5-S6 and S9. Zonal means themselves are produced by the ArcGIS GUI workflow.
"""

import re
from functools import reduce

import pandas as pd

from common import load_settings, resolve_path


FILENAME = re.compile(
    r"^zonal_(WSI|WDEI|WUEI|WESJ|phi_WSI|phi_WDEI|phi_WUEI)_(\d{4})\.csv$"
)


def read_zonal_table(path, unit_field: str) -> pd.DataFrame:
    match = FILENAME.match(path.name)
    if not match:
        raise ValueError(f"Unexpected zonal table name: {path.name}")
    variable, year = match.groups()
    frame = pd.read_csv(path)
    if unit_field not in frame.columns or "MEAN" not in frame.columns:
        raise KeyError(f"{path.name} requires {unit_field} and MEAN fields.")
    output = frame[[unit_field, "MEAN"]].copy()
    output = output.rename(columns={unit_field: "unit_id", "MEAN": variable})
    output["year"] = int(year)
    if "COUNT" in frame.columns:
        output[f"valid_pixels_{variable}"] = frame["COUNT"]
    return output


def main() -> None:
    paths, _ = load_settings()
    unit_field = paths["inputs"]["county_id_field"]
    source_dir = resolve_path(
        paths["inputs"]["tables"]["zonal_statistics_directory"]
    )
    tables = [
        read_zonal_table(path, unit_field)
        for path in sorted(source_dir.glob("zonal_*.csv"))
        if FILENAME.match(path.name)
    ]
    if not tables:
        raise FileNotFoundError(f"No expected zonal CSV files in {source_dir}.")
    merged = reduce(
        lambda left, right: left.merge(
            right, on=["unit_id", "year"], how="outer"
        ),
        tables,
    ).sort_values(["year", "unit_id"])

    output_dir = resolve_path(paths["outputs"]["summary_directory"])
    output_dir.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_dir / "county_year_metrics.csv", index=False)

    annual_columns = [
        column
        for column in ("WSI", "WDEI", "WUEI", "WESJ")
        if column in merged.columns
    ]
    merged.groupby("year")[annual_columns].agg(
        ["count", "mean", "median", "min", "max"]
    ).to_csv(output_dir / "annual_descriptive_statistics.csv")
    print(output_dir)


if __name__ == "__main__":
    main()
