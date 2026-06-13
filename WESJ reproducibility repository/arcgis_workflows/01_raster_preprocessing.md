# ArcGIS Workflow 01: Raster Preprocessing

## Purpose

Prepare all source rasters on one analysis grid before calculating WSI, WRLI,
WDEI, WUEI, or WESJ.

## Inputs

Source rasters, the manuscript reference raster, and the study-area mask.

## Parameters

CRS, cell size, processing extent, Snap Raster, mask, resampling method,
NoData rule, and any documented unit conversion.

## Outputs

Analysis-ready rasters sharing one grid and a private quality-control log.

## Manuscript and SI Correspondence

Supports the pixel-level workflow described in manuscript Section 2.1 and the
input preparation required by Sections 2.2.1-2.3. Variable-specific source and
allocation procedures are documented in Texts S1-S4. This file records the
ArcGIS Pro GUI workflow; it is not presented as an original Python calculation.

## Required ArcGIS Tools

| Step | ArcGIS Pro tool | Key inputs | Key parameters | Output |
|---|---|---|---|---|
| 1 | Define Projection | Raster with missing CRS metadata | Correct source CRS; do not use to reproject | Raster with CRS definition |
| 2 | Project Raster | Source raster and reference raster | Output CRS = reference; Cell Size = reference; Geographic Transformation documented | Reprojected raster |
| 3 | Resample | Reprojected raster | Bilinear for continuous data; Nearest for categorical data | Resampled raster |
| 4 | Extract by Mask | Resampled raster and study boundary | Analysis mask = study boundary | Clipped raster |
| 5 | Set Null / Raster Calculator | Clipped raster | Apply variable-specific invalid-value rules | Analysis-ready raster |

## Environment Settings

Set these under **Analysis > Environments** before every batch:

| Environment | Setting |
|---|---|
| Output Coordinate System | Same as the manuscript reference raster |
| Processing Extent | Same as the reference raster |
| Snap Raster | Reference raster |
| Cell Size | Reference raster |
| Mask | Study boundary or reference valid-data mask |
| Resampling Method | Bilinear for continuous variables; Nearest for classes |
| Parallel Processing Factor | Record the value used locally |

## NoData Handling

1. Preserve source NoData during projection and resampling.
2. Do not convert legitimate zeros to NoData unless the variable definition
   explicitly states that zero is invalid.
3. For denominator layers, set nonpositive values to NoData before division.
4. After preprocessing, verify width, height, CRS, cell size, extent, cell
   origin, and valid-pixel mask.

Example Raster Calculator expression:

```text
SetNull(IsNull("input") | ("input" < valid_minimum), Float("input"))
```

## Quality-Control Record

For each layer and year, record:

- source filename and checksum;
- source CRS, unit, resolution, and NoData definition;
- output CRS, cell size, rows, columns, and extent;
- resampling method;
- valid-pixel count;
- any unit conversion or scaling factor.

Private filenames and checksums should remain in a local, nonpublic log.
