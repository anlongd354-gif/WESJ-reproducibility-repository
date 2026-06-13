from __future__ import annotations

"""Generic ArcPy example for the simplified raster WSI calculation.

Inputs: water-use raster, carrying-capacity raster, and reference raster.
Parameters: alpha, Snap Raster, cell size, extent, mask, and output CRS.
Outputs: one floating-point WSI raster.
Paper/SI: manuscript Section 2.2.1 and Text S5.
Workflow status: reproducible example only; the reported original WSI
calculation was performed through the ArcGIS Pro GUI workflow.
"""

import argparse
from pathlib import Path

import arcpy
from arcpy.sa import Float, IsNull, Raster, SetNull


def calculate_wsi(
    water_use: str,
    carrying_capacity: str,
    output: str,
    alpha: float,
    reference_raster: str,
) -> None:
    if not 0.0 <= alpha < 1.0:
        raise ValueError("alpha must satisfy 0 <= alpha < 1.")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    arcpy.env.overwriteOutput = True
    with arcpy.EnvManager(
        snapRaster=reference_raster,
        cellSize=reference_raster,
        extent=reference_raster,
        mask=reference_raster,
        outputCoordinateSystem=reference_raster,
    ):
        demand = Raster(water_use)
        capacity = Raster(carrying_capacity)
        invalid = (
            IsNull(demand)
            | IsNull(capacity)
            | (demand < 0)
            | (capacity <= 0)
        )
        SetNull(
            invalid,
            Float(demand) / ((1.0 - alpha) * Float(capacity)),
        ).save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="ArcPy WSI example.")
    parser.add_argument("--water-use", required=True)
    parser.add_argument("--carrying-capacity", required=True)
    parser.add_argument("--reference-raster", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--alpha", type=float, default=0.6)
    args = parser.parse_args()

    arcpy.CheckOutExtension("Spatial")
    try:
        calculate_wsi(
            args.water_use,
            args.carrying_capacity,
            args.output,
            args.alpha,
            args.reference_raster,
        )
    finally:
        arcpy.CheckInExtension("Spatial")


if __name__ == "__main__":
    main()
