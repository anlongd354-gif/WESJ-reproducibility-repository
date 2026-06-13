from __future__ import annotations

"""Generic ArcPy example for Global Moran's I and Anselin Local Moran's I.

Inputs: annual polygon features containing a finite WESJ field.
Parameters: Queen/Rook/KNN relationship, row standardization, Euclidean
distance, four neighbors for KNN, and permutation count for LISA.
Outputs: Global Moran summary CSV and LISA feature class.
Paper/SI: manuscript Section 2.1 and Results Section 4.4.2; detailed settings
and robustness checks in Text S8 and Tables S5-S9.
Workflow status: reproducible example only; the reported original analysis was
performed through ArcGIS Pro GUI tools.
"""

import argparse
import csv
from pathlib import Path

import arcpy


RELATIONSHIPS = {
    "queen": "CONTIGUITY_EDGES_CORNERS",
    "rook": "CONTIGUITY_EDGES_ONLY",
    "knn": "K_NEAREST_NEIGHBORS",
}


def run_analysis(
    features: str,
    value_field: str,
    output_directory: str,
    relationship_name: str,
    neighbors: int,
    permutations: int,
) -> None:
    relationship = RELATIONSHIPS[relationship_name]
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    arcpy.env.overwriteOutput = True

    global_result = arcpy.stats.SpatialAutocorrelation(
        features,
        value_field,
        "NO_REPORT",
        relationship,
        "EUCLIDEAN_DISTANCE",
        "ROW",
        "",
        "",
        neighbors if relationship == "K_NEAREST_NEIGHBORS" else "",
    )
    with (output_dir / f"global_moran_{relationship_name}.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["relationship", "moran_i", "z_score", "p_value"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "relationship": relationship_name,
                "moran_i": global_result.getOutput(0),
                "z_score": global_result.getOutput(1),
                "p_value": global_result.getOutput(2),
            }
        )

    lisa_output = str(output_dir / f"lisa_{relationship_name}.shp")
    arcpy.stats.ClustersOutliers(
        features,
        value_field,
        lisa_output,
        relationship,
        "EUCLIDEAN_DISTANCE",
        "ROW",
        "",
        "",
        "NO_FDR",
        permutations,
        neighbors if relationship == "K_NEAREST_NEIGHBORS" else "",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ArcPy Global Moran's I and Anselin Local Moran example."
    )
    parser.add_argument("--features", required=True)
    parser.add_argument("--value-field", default="WESJ")
    parser.add_argument("--output-directory", required=True)
    parser.add_argument(
        "--relationship", choices=sorted(RELATIONSHIPS), default="queen"
    )
    parser.add_argument("--neighbors", type=int, default=4)
    parser.add_argument("--permutations", type=int, default=999)
    args = parser.parse_args()
    run_analysis(
        args.features,
        args.value_field,
        args.output_directory,
        args.relationship,
        args.neighbors,
        args.permutations,
    )


if __name__ == "__main__":
    main()
