from __future__ import annotations

"""Compare WESJ classification schemes without altering continuous WESJ.

Inputs: county statistics table containing `unit_id`, `year`, and `WESJ`.
Parameters: five classes; fixed equal intervals, annual Jenks natural breaks,
and annual quantiles; classes 1-2 identify low WESJ.
Outputs: classification membership CSV and annual break JSON.
Paper/SI: manuscript Section 2.3 and Text S7/Table S2. Classification is not
used to calculate continuous deficit contributions.
"""

import json

import jenkspy
import numpy as np
import pandas as pd

from common import load_settings, resolve_path


def strictly_increasing(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype="float64").copy()
    for index in range(1, len(result)):
        if result[index] <= result[index - 1]:
            result[index] = np.nextafter(result[index - 1], np.inf)
    return result


def calculate_breaks(
    values: np.ndarray,
    method: str,
    classes: int,
    fixed_breaks: list[float],
) -> np.ndarray:
    if method == "equal_interval":
        if fixed_breaks:
            return strictly_increasing(np.asarray(fixed_breaks))
        return np.linspace(float(values.min()), float(values.max()), classes + 1)
    if method == "natural_breaks":
        return strictly_increasing(
            np.asarray(jenkspy.jenks_breaks(values, n_classes=classes))
        )
    if method == "quantile":
        return strictly_increasing(
            np.quantile(values, np.linspace(0.0, 1.0, classes + 1))
        )
    raise ValueError(f"Unknown classification method: {method}")


def classify(values: np.ndarray, breaks: np.ndarray) -> np.ndarray:
    return np.clip(
        np.searchsorted(breaks[1:-1], values, side="right") + 1,
        1,
        len(breaks) - 1,
    )


def main() -> None:
    paths, parameters = load_settings()
    settings = parameters["wesj_classification"]
    source = resolve_path(paths["inputs"]["tables"]["county_statistics"])
    table = pd.read_csv(source)
    required = {"unit_id", "year", "WESJ"}
    if not required.issubset(table.columns):
        raise KeyError(f"County table must contain {sorted(required)}.")

    output_dir = resolve_path(
        paths["outputs"]["classification_sensitivity_directory"]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    classes = int(settings["number_of_classes"])
    low_classes = {int(value) for value in settings["low_wesj_classes"]}
    rows = []
    break_records = []

    for year, group in table.groupby("year"):
        annual = group[np.isfinite(group["WESJ"])].copy()
        values = annual["WESJ"].to_numpy(dtype="float64")
        for method in settings["sensitivity_methods"]:
            breaks = calculate_breaks(
                values,
                method,
                classes,
                settings["baseline_breaks"] if method == "equal_interval" else [],
            )
            labels = classify(values, breaks)
            break_records.append(
                {"year": int(year), "method": method, "breaks": breaks.tolist()}
            )
            for unit_id, wesj, label in zip(
                annual["unit_id"], values, labels
            ):
                rows.append(
                    {
                        "unit_id": unit_id,
                        "year": int(year),
                        "method": method,
                        "WESJ": float(wesj),
                        "class": int(label),
                        "is_low_WESJ": int(label) in low_classes,
                    }
                )

    pd.DataFrame(rows).to_csv(
        output_dir / "classification_results.csv", index=False
    )
    (output_dir / "classification_breaks.json").write_text(
        json.dumps(break_records, indent=2),
        encoding="utf-8",
    )
    print(output_dir)


if __name__ == "__main__":
    main()
