# ArcGIS Workflow 03: WRLI

## Inputs

Population `R`, GDP `Z`, annual precipitation `P`, total water ecosystem
service volume `W`, the reference raster, and the study-area mask.

## Parameters

The piecewise precipitation coefficient `K`, input units, ArcGIS grid
environments, denominator validity rule, and NoData handling.

## Outputs

`wrli_{year}.tif`, the optional precipitation-coefficient raster, and a private
quality-control log.

## Manuscript and SI Correspondence

Manuscript Section 2.2.2, item (1), with gridded water ecosystem service volume
described in Text S3. WRLI was calculated through the ArcGIS Pro GUI workflow;
the ArcPy file is only a reproducible example.

## Formula

```text
C = K * sqrt(R * Z) / W
```

`C` is WRLI, `R` is population in ten thousand persons, `Z` is GDP in billion
CNY, and `W` is total water ecosystem service volume in billion cubic metres.

The precipitation coefficient `K` is:

```text
P <= 200:          1.0
200 <= P <= 400:   1.0 - 0.1 * (P - 200) / 200
400 <= P <= 800:   0.9 - 0.2 * (P - 400) / 400
800 < P <= 1600:   0.7 - 0.2 * (P - 800) / 800
P > 1600:          0.5
```

## ArcGIS Tools

1. Spatial Analyst > Conditional > Con
2. Spatial Analyst > Math > Square Root
3. Spatial Analyst > Map Algebra > Raster Calculator
4. Spatial Analyst > Conditional > Set Null

## Raster Calculator Expressions

Precipitation coefficient:

```text
Con(
  "precipitation" <= 200, 1.0,
  Con(
    "precipitation" <= 400,
    1.0 - 0.1 * ("precipitation" - 200.0) / 200.0,
    Con(
      "precipitation" <= 800,
      0.9 - 0.2 * ("precipitation" - 400.0) / 400.0,
      Con(
        "precipitation" <= 1600,
        0.7 - 0.2 * ("precipitation" - 800.0) / 800.0,
        0.5
      )
    )
  )
)
```

WRLI:

```text
SetNull(
  IsNull("K") |
  IsNull("population") |
  IsNull("gross_domestic_product") |
  IsNull("water_ecosystem_service_volume") |
  ("population" < 0) |
  ("gross_domestic_product" < 0) |
  ("water_ecosystem_service_volume" <= 0),
  Float("K") *
  SquareRoot(Float("population") * Float("gross_domestic_product")) /
  Float("water_ecosystem_service_volume")
)
```

## Output

```text
wrli_{year}.tif
```

The WRLI raster is then passed to `scripts/01_local_gini_wdei.py`.

## Checks

- Precipitation must be in millimetres before applying the coefficient.
- All four inputs must share the reference grid and valid-data mask.
- Record the valid-pixel count and summary statistics for both `K` and WRLI.
