# Reconstruction Instructions

## 1. Obtain Authorized Inputs

Acquire each restricted dataset independently from its original provider under
the applicable access conditions. The authors do not have permission to share
these datasets. Do not place restricted data in the public repository.
Complete `metadata/input_data_metadata.csv` locally with source, access method,
year, resolution, CRS, unit, NoData definition, and preprocessing notes.

## 2. Create Local Configuration

Copy `config/paths_template.yaml` to the ignored
`config/paths_local.yaml`. Populate the year list and private paths. Confirm
all parameters in `config/parameters.yaml` against the final manuscript.

## 3. Reconstruct ArcGIS-derived Layers

Follow the documents in `arcgis_workflows/` in numerical order:

1. project, resample, clip, snap, and mask all input rasters;
2. calculate WSI and its documented normalization;
3. calculate the precipitation coefficient and WRLI;
4. retain a local processing log with ArcGIS version, tool parameters,
   warnings, output statistics, and valid-pixel counts.

The scripts under `scripts_arcpy/` provide generic executable examples of the
same formulas and ArcGIS parameters. The original WSI, WRLI, zonal-statistics,
Moran's I, and LISA calculations were conducted through ArcGIS Pro workflows;
the ArcPy examples do not recharacterize those GUI operations as the original
Python computation. They contain no private path or data.

## 4. Reconstruct Python-derived Layers

Run:

```bash
python scripts/00_validate_inputs.py
python scripts/01_local_gini_wdei.py
python scripts/02_dea_bcc_wuei.py
python scripts/03_entropy_topsis_wesj.py
```

Verify that WDEI and WUEI fall within 0-1 and that the WESJ parameter JSON
records annual entropy weights, vector-normalization denominators, and ideal
solutions.

## 5. Aggregate and Analyze Spatial Patterns

Use ArcGIS **Zonal Statistics as Table** to calculate county means and valid
pixel counts. Export tables using:

```text
zonal_{variable}_{year}.csv
```

Run `scripts/07_generate_summary_tables.py`, join annual WESJ values to the
polygons, and follow `arcgis_workflows/05_spatial_autocorrelation.md` for
Global Moran's I and LISA.

## 6. Reconstruct Sensitivity Analyses

Run:

```bash
python scripts/04_wsi_sensitivity.py
python scripts/05_wesj_classification_sensitivity.py
python scripts/06_wesj_deficit_attribution.py
```

The classification step changes only the set labelled low WESJ. It does not
alter continuous WESJ or contribution values.

The deficit-attribution script must pass:

```text
M1 maximum pixel difference <= 1e-6
decomposition identity error <= 1e-10
```

## 7. Audit the Public Package

Remove all data and results, then run:

```bash
python scripts/99_sanitize_audit.py
```

The public package should contain code, ArcGIS workflow records, parameters,
metadata templates, input contracts, and expected-output descriptions only.
