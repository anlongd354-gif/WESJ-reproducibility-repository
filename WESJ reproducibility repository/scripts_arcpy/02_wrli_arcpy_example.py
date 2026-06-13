from __future__ import annotations

"""Generic ArcPy example for `C = K * sqrt(R * Z) / W`.

Inputs: population, GDP, precipitation, service-volume, and reference rasters.
Parameters: piecewise K rule, Snap Raster, cell size, extent, mask, and
positive denominator requirement.
Outputs: one floating-point WRLI raster.
Paper/SI: manuscript Section 2.2.2, item (1), and Text S3.
Workflow status: reproducible example only; the reported original WRLI
calculation was performed through the ArcGIS Pro GUI workflow.
"""

import argparse
from pathlib import Path

import arcpy
from arcpy.sa import Con, Float, IsNull, Raster, SetNull, SquareRoot


def precipitation_coefficient(precipitation: Raster):
    return Con(
        precipitation <= 200,
        1.0,
        Con(
            precipitation <= 400,
            1.0 - 0.1 * (precipitation - 200.0) / 200.0,
            Con(
                precipitation <= 800,
                0.9 - 0.2 * (precipitation - 400.0) / 400.0,
                Con(
                    precipitation <= 1600,
                    0.7 - 0.2 * (precipitation - 800.0) / 800.0,
                    0.5,
                ),
            ),
        ),
    )


def calculate_wrli(
    population_path: str,
    gdp_path: str,
    precipitation_path: str,
    service_volume_path: str,
    output: str,
    reference_raster: str,
) -> None:
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    arcpy.env.overwriteOutput = True
    with arcpy.EnvManager(
        snapRaster=reference_raster,
        cellSize=reference_raster,
        extent=reference_raster,
        mask=reference_raster,
        outputCoordinateSystem=reference_raster,
    ):
        population = Raster(population_path)
        gdp = Raster(gdp_path)
        precipitation = Raster(precipitation_path)
        service = Raster(service_volume_path)
        coefficient = precipitation_coefficient(precipitation)
        invalid = (
            IsNull(population)
            | IsNull(gdp)
            | IsNull(precipitation)
            | IsNull(service)
            | (population < 0)
            | (gdp < 0)
            | (service <= 0)
        )
        wrli = Float(coefficient) * SquareRoot(
            Float(population) * Float(gdp)
        ) / Float(service)
        SetNull(invalid, wrli).save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="ArcPy WRLI example.")
    parser.add_argument("--population", required=True)
    parser.add_argument("--gdp", required=True)
    parser.add_argument("--precipitation", required=True)
    parser.add_argument("--service-volume", required=True)
    parser.add_argument("--reference-raster", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    arcpy.CheckOutExtension("Spatial")
    try:
        calculate_wrli(
            args.population,
            args.gdp,
            args.precipitation,
            args.service_volume,
            args.output,
            args.reference_raster,
        )
    finally:
        arcpy.CheckInExtension("Spatial")


if __name__ == "__main__":
    main()
