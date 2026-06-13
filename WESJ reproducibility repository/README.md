# Water Ecosystem Service Justice Reproducibility Workflow

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![ArcGIS Pro 3.4.2](https://img.shields.io/badge/ArcGIS_Pro-3.4.2-2C7AC3)
![Reproducibility](https://img.shields.io/badge/package-reproducibility-2E8B57)
![Data availability](https://img.shields.io/badge/study_data-not_included-lightgrey)

This repository provides the documented computational workflow for constructing
and evaluating Water Ecosystem Service Justice (WESJ) indicators. It combines
ArcGIS Pro procedures, Python scripts, public parameter files, metadata
templates, input contracts, sensitivity analyses, and deficit attribution.

> [!IMPORTANT]
> This repository contains **no original or derived study data**. It reproduces
> the calculation procedures, not the right to access or redistribute the
> restricted source datasets.

## Start Here

| Goal | Resource |
|---|---|
| Understand the reproducibility scope | [Reproducibility Boundary](#reproducibility-boundary) |
| Reconstruct the workflow | [`RECONSTRUCTION.md`](RECONSTRUCTION.md) |
| Review data-sharing restrictions | [`DATA_POLICY.md`](DATA_POLICY.md) |
| Prepare local inputs | [`input_templates/`](input_templates/) and [`metadata/`](metadata/) |
| Review ArcGIS procedures | [`arcgis_workflows/`](arcgis_workflows/) |
| Run the Python stages | [`scripts/`](scripts/) |
| Inspect expected outputs | [`outputs_expected/`](outputs_expected/) |
| Audit a public release | [`AUTHOR_CHECKLIST.md`](AUTHOR_CHECKLIST.md) |

## Workflow Coverage

| Stage | Method | Primary implementation |
|---|---|---|
| Water stress | WSI | ArcGIS Pro workflow and ArcPy example |
| Water resource load | WRLI | ArcGIS Pro workflow and ArcPy example |
| Distributional equity | Local Gini-based WDEI | Python |
| Use efficiency | Input-oriented DEA-BCC WUEI | Python |
| Composite justice index | Entropy-weighted TOPSIS WESJ | Python |
| Spatial patterns | Global Moran's I and LISA | ArcGIS Pro |
| Robustness | Parameter, composition, classification, and model sensitivity | Python and ArcGIS Pro |
| Deficit attribution | Fixed-parameter TOPSIS-Shapley | Python |

## Purpose

The package is intended for readers who independently obtain the required
inputs from the original data providers. They may then use the documented
ArcGIS procedures, parameter files, metadata templates, and Python scripts to
reconstruct the main derived layers and index calculations. Nothing in this
repository implies that the source data are publicly available or may be
redistributed by the authors.

## Reproducibility Boundary

The workflow reproduces calculation procedures, not data access rights.

- No restricted raster, vector, spreadsheet, database, administrative name,
  machine-specific path, or numerical study result is included.
- `config/paths_local.yaml`, `data/`, `outputs/`, `scratch/`, and local logs are
  excluded from version control.
- Public templates retain only variable names, units, years, parameters, and
  generic filename patterns.
- WSI, WRLI, zonal statistics, Global Moran's I, and LISA were performed in
  ArcGIS Pro and are documented as ArcGIS workflows. Example ArcPy scripts are
  supplied as executable records, not as claims that the original GUI
  operations were performed in Python.

## Software Environment

ArcGIS stages were documented for:

```text
ArcGIS Pro 3.4.2
Spatial Analyst extension
Spatial Statistics Tools
```

Python stages require Python 3.11 and the packages in `environment.yml` or
`requirements.txt`. ArcPy is supplied by ArcGIS Pro and must not be installed
from PyPI.

## Repository Structure

```text
.
|-- README.md
|-- RECONSTRUCTION.md
|-- DATA_POLICY.md
|-- environment.yml
|-- requirements.txt
|-- metadata/
|   |-- input_data_metadata.csv
|   |-- variable_dictionary.csv
|   `-- parameter_settings.csv
|-- config/
|   |-- paths_template.yaml
|   `-- parameters.yaml
|-- arcgis_workflows/
|   |-- 01_raster_preprocessing.md
|   |-- 02_wsi_raster_calculator.md
|   |-- 03_wrli_raster_calculator.md
|   |-- 04_zonal_statistics.md
|   `-- 05_spatial_autocorrelation.md
|-- scripts/
|   |-- 00_validate_inputs.py
|   |-- 01_local_gini_wdei.py
|   |-- 02_dea_bcc_wuei.py
|   |-- 03_entropy_topsis_wesj.py
|   |-- 04_wsi_sensitivity.py
|   |-- 05_wesj_classification_sensitivity.py
|   |-- 06_wesj_deficit_attribution.py
|   |-- 07_generate_summary_tables.py
|   `-- 99_sanitize_audit.py
|-- scripts_arcpy/
|   |-- 01_wsi_arcpy_example.py
|   |-- 02_wrli_arcpy_example.py
|   `-- 03_spatial_autocorrelation_arcpy_example.py
|-- input_templates/
|   |-- county_statistics_template.csv
|   |-- raster_file_naming_rules.md
|   `-- expected_input_layers.md
`-- outputs_expected/
    |-- README.md
    `-- output_fields.csv
```

## Manuscript and SI Crosswalk

| Repository file | Method or record | Manuscript/SI correspondence |
|---|---|---|
| `arcgis_workflows/01_raster_preprocessing.md` | Projection, resampling, clipping, Snap Raster, and NoData | Section 2.1; input preparation for Sections 2.2.1-2.3; Texts S1-S4 |
| `arcgis_workflows/02_wsi_raster_calculator.md` | Original and simplified WSI formulas and Raster Calculator expressions | Section 2.2.1; Texts S1-S2 and S5 |
| `arcgis_workflows/03_wrli_raster_calculator.md` | WRLI and precipitation coefficient | Section 2.2.2; Text S3 |
| `scripts/01_local_gini_wdei.py` | Local Gini-based WDEI | Section 2.2.2; Text S6 and Table S1 |
| `scripts/02_dea_bcc_wuei.py` | Input-oriented DEA-BCC WUEI | Section 2.2.3 and Table 1; Text S4 |
| `scripts/03_entropy_topsis_wesj.py` | Entropy-weighted vector-TOPSIS WESJ | Section 2.3 |
| `arcgis_workflows/04_zonal_statistics.md` | County-level zonal means | Sections 2.1-2.3; Texts S5-S6 and S9 |
| `arcgis_workflows/05_spatial_autocorrelation.md` | Global Moran's I and LISA | Section 2.1, Results Section 4.4.2; Text S8 and Tables S5-S9 |
| `scripts/04_wsi_sensitivity.py` | Alpha and water-demand-composition checks | Section 2.2.1; Text S5 |
| `scripts/05_wesj_classification_sensitivity.py` | Equal interval, natural breaks, and quantile | Section 2.3; Text S7 and Table S2 |
| `scripts/06_wesj_deficit_attribution.py` | M1-M7 and fixed-parameter TOPSIS-Shapley | Section 2.3; Text S9 |
| `scripts/07_generate_summary_tables.py` | Merge ArcGIS zonal-statistics exports | County aggregation used across Sections 2.2.1-2.3 and Texts S5-S9 |

The ArcPy files mirror selected ArcGIS formulas and tool parameters as generic
examples. They do not imply that the original ArcGIS Pro GUI calculations were
performed in Python.

## Reconstruction Templates

The following directories are intentionally retained even though no study data
are distributed:

| Directory | Reconstruction role |
|---|---|
| `input_templates/` | Defines required fields, expected layers, units, years, and generic filename rules |
| `metadata/` | Records provider, access condition, temporal coverage, resolution, CRS, units, variable meaning, and parameters |
| `config/` | Separates public method parameters from the untracked local path configuration |
| `outputs_expected/` | Defines expected filenames, output fields, ranges, and interpretation without including results |

Together, these files explain how readers who independently obtain the required
source data can prepare inputs and reconstruct the analytical products. They do
not provide or promise access to the restricted source data.

## Calculation Sequence

1. **Prepare and document inputs.** Complete the metadata templates locally and
   place authorized source data under an ignored private directory.
2. **Align rasters in ArcGIS Pro.** Set the reference CRS, cell size, extent,
   Snap Raster, mask, resampling method, and NoData rules.
3. **Calculate WSI in ArcGIS Pro.**

   The original formulation in manuscript Section 2.2.1 is:

   ```text
   WSI = WEF / WEC = W_i,c / ((1 - alpha) * phi * Q_c)
   ```

   The simplified raster formulation used for the main WSI calculation is:

   ```text
   WSI = W_i,c / ((1 - alpha) * Q_c)
   ```

   Here, `W_i,c` is agricultural water use in raster cell `i` for the main
   calculation, `Q_c` is water ecosystem service carrying capacity, `alpha`
   is the availability correction coefficient, and `phi` is the
   category-specific production coefficient omitted from the simplified
   baseline. The baseline uses `alpha = 0.6`. Original-versus-simplified,
   `alpha`, `phi`, and water-demand-composition checks are documented in Text
   S5. Domestic and ecological water use are included only in the additional
   demand-composition sensitivity test.
4. **Calculate WRLI in ArcGIS Pro.**

   ```text
   C = K * sqrt(R * Z) / W
   ```

   Here, `C` is WRLI, `K` is the precipitation coefficient, `R` is population
   in ten thousand persons, `Z` is GDP in billion CNY, and `W` is total water
   ecosystem service volume in billion cubic metres. This matches manuscript
   Section 2.2.2. The complete piecewise precipitation coefficient is recorded
   in `config/parameters.yaml` and the ArcGIS workflow.
5. **Calculate WDEI in Python.** `01_local_gini_wdei.py` applies the Local Gini
   formula to valid WRLI pixels in the configured moving window.
6. **Calculate WUEI in Python.** `02_dea_bcc_wuei.py` uses cropland ratio as
   the template grid, aligns population density, water consumption, and
   ecosystem service value by bilinear `WarpedVRT` while retaining legitimate
   zeros, and solves an input-oriented DEA-BCC model with variable returns to
   scale in `512 x 512` tiles with a five-pixel halo.
7. **Calculate WESJ in Python.** `03_entropy_topsis_wesj.py` applies component
   direction conversion, min-max preprocessing for entropy weights, vector
   normalization for TOPSIS, and relative closeness calculation.
8. **Aggregate in ArcGIS Pro.** Zonal Statistics as Table calculates county
   means and valid-pixel counts.
9. **Run spatial autocorrelation in ArcGIS Pro.** Global Moran's I and Anselin
   Local Moran's I use row-standardized Queen contiguity at baseline, with
   Rook and four-nearest-neighbor sensitivity checks.
10. **Run sensitivity and attribution analyses.** WSI parameter/composition,
    WESJ classification, seven continuous model specifications, and
    fixed-parameter TOPSIS-Shapley attribution are evaluated separately.

## Prepare Local Inputs

Create the private path configuration:

```bash
cp config/paths_template.yaml config/paths_local.yaml
```

On Windows PowerShell:

```powershell
Copy-Item config/paths_template.yaml config/paths_local.yaml
```

Edit only `config/paths_local.yaml`. Set the study years and local paths. Do
not commit this file. Follow the naming and layer contracts under
`input_templates/`.

## Install Python Dependencies

```bash
conda env create -f environment.yml
conda activate wesj-reproducibility
```

Or install into a compatible environment:

```bash
python -m pip install -r requirements.txt
```

## Run the Python Stages

After the ArcGIS preprocessing, WSI, and WRLI outputs exist:

```bash
python scripts/00_validate_inputs.py
python scripts/01_local_gini_wdei.py
python scripts/02_dea_bcc_wuei.py
python scripts/03_entropy_topsis_wesj.py
python scripts/04_wsi_sensitivity.py
python scripts/06_wesj_deficit_attribution.py
```

After ArcGIS Zonal Statistics tables are exported:

```bash
python scripts/07_generate_summary_tables.py
python scripts/05_wesj_classification_sensitivity.py
```

The stages are intentionally explicit rather than hidden behind a single
command, because ArcGIS operations and restricted local inputs require
author-side verification between stages.

## Key Methodological Safeguards

- M1 in `06_wesj_deficit_attribution.py` must reproduce the manuscript WESJ
  raster within a maximum absolute pixel difference of `1e-6`; otherwise the
  script stops.
- TOPSIS-Shapley counterfactuals hold weights, vector-normalization
  denominators, positive and negative ideals, indicator directions, and the
  valid-pixel mask fixed.
- Classification is used only to identify low-WESJ units. It is not used to
  calculate continuous component-deficit contributions.
- M4-M6 are weighted-arithmetic-mean controls and do not replace the formal
  baseline WESJ model.

## Interpreting Outputs

WESJ and WUEI are benefit-oriented: larger values indicate better performance.
WSI and WDEI are cost-oriented before positive orientation.

`phi_WSI`, `phi_WDEI`, and `phi_WUEI` are absolute contributions to the
continuous WESJ deficit. Contribution shares are obtained only after summing
absolute contributions over the stated spatial and temporal unit.

The attribution script writes a wording recommendation:

- all seven models support WUEI dominance: "under all tested specifications";
- a majority support it: "under most tested specifications";
- otherwise: "under the baseline and several sensitivity specifications".

## Public-Release Audit

Add any private study names, provider identifiers, or administrative names to
the untracked `config/sensitive_terms.local.txt`, one term per line, then run:

```bash
python scripts/99_sanitize_audit.py
```

Review `AUTHOR_CHECKLIST.md` before repository deposit.
