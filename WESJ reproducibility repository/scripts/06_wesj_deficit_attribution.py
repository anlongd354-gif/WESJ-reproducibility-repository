from __future__ import annotations

"""Run M1-M7 WESJ robustness models and component-deficit attribution.

Inputs: aligned normalized WSI, WDEI, WUEI, and baseline manuscript WESJ
rasters.
Parameters: entropy/equal/CRITIC weights, TOPSIS or weighted mean, original or
min-max positive scores, and fixed-parameter TOPSIS-Shapley counterfactuals.
Outputs: model WESJ/contribution rasters, annual and period summaries,
validation tables, and wording recommendation.
Paper/SI: manuscript Section 2.3 and the attribution paragraph following Table
2; full definitions and aggregation formulas in Text S9.
"""

import math
from itertools import combinations

import numpy as np
import pandas as pd

from common import (
    EPS,
    assert_same_grid,
    format_path,
    load_settings,
    minmax_columns,
    read_raster,
    resolve_path,
    write_raster,
    years_from_paths,
)


COMPONENTS = ("WSI", "WDEI", "WUEI")
M1_TOLERANCE = 1e-6
IDENTITY_TOLERANCE = 1e-10


def positive_scores(
    wsi: np.ndarray, wdei: np.ndarray, wuei: np.ndarray
) -> np.ndarray:
    return np.column_stack(
        [
            1.0 - np.clip(wsi, 0.0, 1.0),
            1.0 - np.clip(wdei, 0.0, 1.0),
            np.clip(wuei, 0.0, 1.0),
        ]
    )


def entropy_weights(values: np.ndarray) -> np.ndarray:
    normalized = np.clip(minmax_columns(values), EPS, 1.0)
    proportions = normalized / np.sum(normalized, axis=0)
    entropy = -(1.0 / math.log(values.shape[0])) * np.sum(
        proportions * np.log(proportions), axis=0
    )
    divergence = 1.0 - entropy
    return (
        divergence / np.sum(divergence)
        if np.sum(divergence) > EPS
        else np.full(values.shape[1], 1.0 / values.shape[1])
    )


def critic_weights(values: np.ndarray) -> np.ndarray:
    normalized = minmax_columns(values)
    standard_deviation = np.std(normalized, axis=0, ddof=0)
    correlation = np.corrcoef(normalized, rowvar=False)
    correlation = np.nan_to_num(correlation, nan=0.0)
    np.fill_diagonal(correlation, 1.0)
    information = standard_deviation * np.sum(1.0 - correlation, axis=1)
    return (
        information / np.sum(information)
        if np.sum(information) > EPS
        else np.full(values.shape[1], 1.0 / values.shape[1])
    )


def weights_for(values: np.ndarray, method: str) -> np.ndarray:
    if method == "entropy":
        return entropy_weights(values)
    if method == "equal":
        return np.full(values.shape[1], 1.0 / values.shape[1])
    if method == "critic":
        return critic_weights(values)
    raise ValueError(method)


def topsis_parameters(
    values: np.ndarray, weights: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    denominator = np.sqrt(np.sum(values**2, axis=0))
    denominator = np.where(denominator <= EPS, 1.0, denominator)
    weighted = values / denominator * weights
    positive = np.max(weighted, axis=0)
    negative = np.min(weighted, axis=0)
    return weighted, denominator, positive, negative


def topsis_score(
    weighted: np.ndarray, positive: np.ndarray, negative: np.ndarray
) -> np.ndarray:
    distance_positive = np.sqrt(np.sum((weighted - positive) ** 2, axis=1))
    distance_negative = np.sqrt(np.sum((weighted - negative) ** 2, axis=1))
    return distance_negative / (
        distance_positive + distance_negative + EPS
    )


def fixed_parameter_shapley(
    weighted: np.ndarray, positive: np.ndarray, negative: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    player_count = weighted.shape[1]
    values = np.empty((1 << player_count, weighted.shape[0]), dtype="float64")
    for subset in range(1 << player_count):
        counterfactual = np.broadcast_to(positive, weighted.shape).copy()
        for player in range(player_count):
            if subset & (1 << player):
                counterfactual[:, player] = weighted[:, player]
        values[subset] = 1.0 - topsis_score(
            counterfactual, positive, negative
        )
    values[0] = 0.0

    contributions = np.zeros_like(weighted)
    players = set(range(player_count))
    for player in range(player_count):
        others = players - {player}
        for subset_size in range(player_count):
            coefficient = (
                math.factorial(subset_size)
                * math.factorial(player_count - subset_size - 1)
                / math.factorial(player_count)
            )
            for subset_items in combinations(others, subset_size):
                subset = sum(1 << item for item in subset_items)
                contributions[:, player] += coefficient * (
                    values[subset | (1 << player)] - values[subset]
                )
    full_deficit = values[(1 << player_count) - 1]
    return contributions, full_deficit


def validate_m1(
    calculated: np.ndarray,
    valid: np.ndarray,
    profile: dict,
    existing_path,
) -> float:
    existing, existing_valid, existing_profile = read_raster(existing_path)
    assert_same_grid([profile, existing_profile])
    common = valid & existing_valid
    if not np.array_equal(valid, existing_valid):
        raise RuntimeError("M1 valid-pixel mask differs from baseline WESJ.")
    difference = float(np.max(np.abs(calculated[common] - existing[common])))
    if difference > M1_TOLERANCE:
        raise RuntimeError(
            f"M1 does not reproduce baseline WESJ: max difference={difference}"
        )
    return difference


def main() -> None:
    paths, parameters = load_settings()
    models = parameters["wesj_method_sensitivity"]["models"]
    derived = paths["inputs"]["derived_rasters"]
    output_dir = resolve_path(paths["outputs"]["deficit_attribution_directory"])
    raster_dir = output_dir / "rasters"
    raster_dir.mkdir(parents=True, exist_ok=True)

    annual_rows = []
    validation_rows = []
    period_totals = {
        model: np.zeros(len(COMPONENTS), dtype="float64") for model in models
    }

    for year in years_from_paths(paths):
        sources = [
            format_path(derived["wsi_normalized"], year=year),
            format_path(paths["outputs"]["wdei_pattern"], year=year),
            format_path(paths["outputs"]["wuei_pattern"], year=year),
        ]
        loaded = [read_raster(source) for source in sources]
        assert_same_grid([item[2] for item in loaded])
        valid = np.logical_and.reduce([item[1] for item in loaded])
        original = positive_scores(
            loaded[0][0][valid],
            loaded[1][0][valid],
            loaded[2][0][valid],
        )
        minmax = minmax_columns(original)

        for model, specification in models.items():
            values = (
                original
                if specification["preprocessing"] == "original_positive"
                else minmax
            )
            weights = weights_for(values, specification["weighting"])
            if specification["aggregation"] == "topsis":
                weighted, _, positive, negative = topsis_parameters(
                    values, weights
                )
                wesj_values = topsis_score(weighted, positive, negative)
                contributions, deficit = fixed_parameter_shapley(
                    weighted, positive, negative
                )
            else:
                wesj_values = values @ weights
                contributions = (1.0 - values) * weights
                deficit = 1.0 - wesj_values

            identity_error = float(
                np.max(np.abs(contributions.sum(axis=1) - deficit))
            )
            if identity_error > IDENTITY_TOLERANCE:
                raise RuntimeError(
                    f"{year} {model}: decomposition identity failed: "
                    f"{identity_error}"
                )

            wesj_raster = np.full(valid.shape, np.nan, dtype="float64")
            wesj_raster[valid] = wesj_values
            if model == "M1":
                m1_difference = validate_m1(
                    wesj_raster,
                    valid,
                    loaded[0][2],
                    format_path(derived["wesj_baseline"], year=year),
                )
            else:
                m1_difference = np.nan

            write_raster(
                raster_dir / f"{model}_wesj_{year}.tif",
                wesj_raster,
                loaded[0][2],
            )
            totals = np.sum(contributions, axis=0)
            shares = totals / np.sum(totals) * 100.0
            period_totals[model] += totals
            for component_index, component in enumerate(COMPONENTS):
                raster = np.full(valid.shape, np.nan, dtype="float64")
                raster[valid] = contributions[:, component_index]
                write_raster(
                    raster_dir / f"{model}_phi_{component}_{year}.tif",
                    raster,
                    loaded[0][2],
                )

            annual_rows.append(
                {
                    "year": year,
                    "model": model,
                    "preprocessing": specification["preprocessing"],
                    "weighting": specification["weighting"],
                    "aggregation": specification["aggregation"],
                    "weight_WSI": weights[0],
                    "weight_WDEI": weights[1],
                    "weight_WUEI": weights[2],
                    "share_WSI": shares[0],
                    "share_WDEI": shares[1],
                    "share_WUEI": shares[2],
                }
            )
            validation_rows.append(
                {
                    "year": year,
                    "model": model,
                    "identity_error": identity_error,
                    "M1_max_pixel_difference": m1_difference,
                }
            )

    period_rows = []
    for model, totals in period_totals.items():
        shares = totals / np.sum(totals) * 100.0
        period_rows.append(
            {
                "model": model,
                "share_WSI": shares[0],
                "share_WDEI": shares[1],
                "share_WUEI": shares[2],
                "largest_component": COMPONENTS[int(np.argmax(totals))],
            }
        )
    wuei_largest = sum(
        row["largest_component"] == "WUEI" for row in period_rows
    )
    if wuei_largest == len(period_rows):
        wording = (
            "WUEI-related deficits remained the largest contributor under "
            "all tested specifications."
        )
    elif wuei_largest >= math.ceil(len(period_rows) / 2):
        wording = (
            "WUEI-related deficits remained the largest contributor under "
            "most tested specifications."
        )
    else:
        wording = (
            "WUEI-related deficits remained the largest contributor under "
            "the baseline and several sensitivity specifications."
        )

    pd.DataFrame(annual_rows).to_csv(
        output_dir / "annual_model_summary.csv", index=False
    )
    pd.DataFrame(period_rows).to_csv(
        output_dir / "period_model_summary.csv", index=False
    )
    pd.DataFrame(validation_rows).to_csv(
        output_dir / "validation_summary.csv", index=False
    )
    (output_dir / "recommended_wording.txt").write_text(
        wording + "\n", encoding="utf-8"
    )
    print(output_dir)


if __name__ == "__main__":
    main()
