# ArcGIS Workflow 04: Zonal Statistics as Table

## Purpose

Aggregate pixel-level WSI, WDEI, WUEI, WESJ, and component-deficit
contributions to anonymous administrative units.

## Inputs

Administrative polygons with a stable `unit_id` and one annual index or
contribution raster at a time.

## Parameters

Zone field, `DATA` NoData handling, `MEAN` statistic, and the raster-specific
processing year.

## Outputs

Annual zonal-statistics tables containing `unit_id`, `MEAN`, and `COUNT`.

## Manuscript and SI Correspondence

Supports county-level aggregation in manuscript Sections 2.1, 2.2.2, 2.2.3,
and 2.3; WSI comparisons in Text S5; Local Gini comparisons in Text S6; and
county-level contribution aggregation in Text S9. This is an ArcGIS Pro GUI
workflow, not an original Python calculation.

## Tool

**Spatial Analyst > Zonal > Zonal Statistics as Table**

## Parameters

| Parameter | Setting |
|---|---|
| Input raster or feature zone data | Administrative polygons |
| Zone field | Stable integer `unit_id` |
| Input value raster | One index or contribution raster for one year |
| Ignore NoData in calculations | DATA |
| Statistics type | MEAN |
| Process as multidimensional | CURRENT_SLICE unless explicitly required |

Run separately for each variable and year. Use **Join Field** or a scripted
table merge to combine outputs by `unit_id` and `year`.

## Outputs

Suggested private table names:

```text
zonal_WSI_{year}
zonal_WDEI_{year}
zonal_WUEI_{year}
zonal_WESJ_{year}
zonal_phi_WSI_{year}
zonal_phi_WDEI_{year}
zonal_phi_WUEI_{year}
```

## Checks

- Use the same administrative boundary version for every year.
- Preserve the stable anonymous identifier; administrative names are not
  required by the public workflow.
- Export `COUNT` with `MEAN` and retain it as the valid-pixel count.
- Do not replace NoData county means with zero.
