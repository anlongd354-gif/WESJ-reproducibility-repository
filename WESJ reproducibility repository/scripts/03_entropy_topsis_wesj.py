from __future__ import annotations

"""Construct annual WESJ using the manuscript entropy-weighted TOPSIS model.

Inputs: normalized WSI, Local Gini-based WDEI, and DEA-BCC WUEI rasters.
Parameters: WSI/WDEI cost directions, WUEI benefit direction, min-max
preprocessing for entropy weights, and vector-normalized TOPSIS.
Outputs: annual WESJ rasters and JSON files recording weights and TOPSIS
parameters.
Paper/SI: manuscript Section 2.3; classification sensitivity is handled
separately in Text S7.
"""

import math

import numpy as np

from common import (
    EPS,
    assert_same_grid,
    format_path,
    load_settings,
    minmax_columns,
    read_raster,
    write_json,
    write_raster,
    years_from_paths,
)


COMPONENTS = ("WSI", "WDEI", "WUEI")


def orient_components(
    wsi: np.ndarray, wdei: np.ndarray, wuei: np.ndarray
) -> np.ndarray:
    return np.column_stack(
        [
            1.0 - np.clip(wsi, 0.0, 1.0),
            1.0 - np.clip(wdei, 0.0, 1.0),
            np.clip(wuei, 0.0, 1.0),
        ]
    )


def entropy_weights(scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if scores.shape[0] < 2:
        raise ValueError("Entropy weighting requires at least two valid pixels.")
    entropy_input = np.clip(minmax_columns(scores), EPS, 1.0)
    proportions = entropy_input / np.sum(entropy_input, axis=0)
    entropy = -(1.0 / math.log(scores.shape[0])) * np.sum(
        proportions * np.log(proportions), axis=0
    )
    divergence = 1.0 - entropy
    weights = (
        divergence / np.sum(divergence)
        if np.sum(divergence) > EPS
        else np.full(scores.shape[1], 1.0 / scores.shape[1])
    )
    return weights, entropy


def vector_topsis(
    scores: np.ndarray, weights: np.ndarray
) -> tuple[np.ndarray, dict[str, list[float]]]:
    denominator = np.sqrt(np.sum(scores**2, axis=0))
    denominator = np.where(denominator <= EPS, 1.0, denominator)
    weighted = scores / denominator * weights
    positive_ideal = np.max(weighted, axis=0)
    negative_ideal = np.min(weighted, axis=0)
    distance_positive = np.sqrt(
        np.sum((weighted - positive_ideal) ** 2, axis=1)
    )
    distance_negative = np.sqrt(
        np.sum((weighted - negative_ideal) ** 2, axis=1)
    )
    total = distance_positive + distance_negative
    closeness = np.divide(
        distance_negative,
        total,
        out=np.ones_like(total),
        where=total > EPS,
    )
    return closeness, {
        "vector_normalization_denominator": denominator.tolist(),
        "positive_ideal": positive_ideal.tolist(),
        "negative_ideal": negative_ideal.tolist(),
    }


def main() -> None:
    paths, parameters = load_settings()
    directions = parameters["entropy_topsis_wesj"]["directions"]
    if directions != {"WSI": "cost", "WDEI": "cost", "WUEI": "benefit"}:
        raise ValueError("Configured component directions do not match the method.")

    derived = paths["inputs"]["derived_rasters"]
    for year in years_from_paths(paths):
        sources = [
            format_path(derived["wsi_normalized"], year=year),
            format_path(paths["outputs"]["wdei_pattern"], year=year),
            format_path(paths["outputs"]["wuei_pattern"], year=year),
        ]
        loaded = [read_raster(source) for source in sources]
        assert_same_grid([item[2] for item in loaded])
        valid = np.logical_and.reduce([item[1] for item in loaded])
        scores = orient_components(
            loaded[0][0][valid],
            loaded[1][0][valid],
            loaded[2][0][valid],
        )
        weights, entropy = entropy_weights(scores)
        closeness, topsis_parameters = vector_topsis(scores, weights)

        wesj = np.full(valid.shape, np.nan, dtype="float64")
        wesj[valid] = closeness
        write_raster(
            format_path(paths["outputs"]["wesj_pattern"], year=year),
            wesj,
            loaded[0][2],
        )
        write_json(
            format_path(
                paths["outputs"]["wesj_parameters_pattern"], year=year
            ),
            {
                "year": year,
                "components": list(COMPONENTS),
                "directions": directions,
                "weights": weights.tolist(),
                "entropy": entropy.tolist(),
                **topsis_parameters,
            },
        )
        print(f"{year}: entropy-weighted vector-TOPSIS WESJ written.")


if __name__ == "__main__":
    main()
