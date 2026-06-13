# ArcGIS Workflow 02: WSI

## Inputs

Agricultural water use `W_i,c`, water ecosystem service carrying capacity
`Q_c`, the reference raster, and the study-area mask. Domestic and ecological
water-use rasters are used only for the additional composition sensitivity.

## Parameters

Baseline `alpha = 0.6`; the original formulation also contains the uniform
category-specific coefficient `phi`. ArcGIS environment settings must match
the reference raster.

## Outputs

`wsi_{year}.tif`, `wsi_normalized_{year}.tif`, and a private calculation log.

## Manuscript and SI Correspondence

Manuscript Section 2.2.1; input allocation in Texts S1-S2; original versus
simplified formulation, `alpha`, `phi`, and demand-composition sensitivity in
Text S5. The original calculations were conducted through ArcGIS Pro GUI
operations. The ArcPy file is only a reproducible example.

## Formula

The original formulation in the manuscript is:

```text
WSI = WEF / WEC = W_i,c / ((1 - alpha) * phi * Q_c)
```

The simplified raster formulation used for the main calculation is:

```text
WSI = W_i,c / ((1 - alpha) * Q_c)
```

The main numerator is agricultural water use. The sum of agricultural,
domestic, and ecological water use is evaluated only in Text S5.

## ArcGIS Tools and Settings

| Item | Setting |
|---|---|
| Tool | Spatial Analyst > Map Algebra > Raster Calculator |
| Snap Raster | Reference raster |
| Cell Size | Reference raster |
| Extent | Reference raster |
| Mask | Study boundary |
| Output type | Floating point raster |

## Raster Calculator Expressions

Original formulation used for the Text S5 comparison, with `PHI` replaced by
the documented uniform scenario value:

```text
SetNull(
  IsNull("agricultural_water_use") |
  IsNull("water_carrying_capacity") |
  ("agricultural_water_use" < 0) |
  ("water_carrying_capacity" <= 0),
  Float("agricultural_water_use") /
  ((1.0 - 0.6) * PHI * Float("water_carrying_capacity"))
)
```

Simplified main formulation:

```text
SetNull(
  IsNull("agricultural_water_use") |
  IsNull("water_carrying_capacity") |
  ("agricultural_water_use" < 0) |
  ("water_carrying_capacity" <= 0),
  Float("agricultural_water_use") /
  ((1.0 - 0.6) * Float("water_carrying_capacity"))
)
```

Total-water-use numerator:

```text
SetNull(
  IsNull("agricultural_water_use") |
  IsNull("domestic_water_use") |
  IsNull("ecological_water_use") |
  IsNull("water_carrying_capacity") |
  ("water_carrying_capacity" <= 0),
  (
    Float("agricultural_water_use") +
    Float("domestic_water_use") +
    Float("ecological_water_use")
  ) /
  ((1.0 - 0.6) * Float("water_carrying_capacity"))
)
```

For the normalized WSI input used by WESJ, obtain the documented annual
minimum and maximum with **Get Raster Properties**, then calculate:

```text
Float("WSI" - WSI_MIN) / Float(WSI_MAX - WSI_MIN)
```

## Outputs

```text
wsi_{year}.tif
wsi_normalized_{year}.tif
```

## Checks

- Confirm identical units in numerator and denominator.
- Confirm `alpha` and numerator composition match the manuscript baseline.
- Confirm nonpositive denominator cells are NoData.
- Record annual minimum, maximum, mean, valid-pixel count, and formula variant.
