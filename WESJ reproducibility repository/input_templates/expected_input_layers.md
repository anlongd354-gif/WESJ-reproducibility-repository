# Expected Input Layers

## ArcGIS-derived inputs

| Layer | Required content | Used by |
|---|---|---|
| `wsi_normalized_{year}.tif` | WSI normalized to 0-1 | WESJ |
| `wrli_{year}.tif` | WRLI calculated with the documented coefficient rule | WDEI |
| Administrative polygons | Stable integer `unit_id` field | Zonal statistics and spatial autocorrelation |

## Python-stage inputs

| Layer | Required content | Used by |
|---|---|---|
| `population_density_{year}.tif` | Nonnegative continuous values | DEA-BCC WUEI input |
| `water_consumption_{year}.tif` | Nonnegative continuous values | DEA-BCC WUEI input |
| `cropland_ratio_{year}.tif` | Values in 0-1 or documented equivalent | DEA-BCC WUEI input |
| `ecosystem_service_value_{year}.tif` | Nonnegative continuous values | DEA-BCC WUEI output |

For WUEI, `cropland_ratio_{year}.tif` is the template grid. The other three
layers are aligned to it with bilinear resampling by the original workflow.
Legitimate zero values are retained. Other index layers must share the
reference grid. Restricted layers are not included in this repository.
