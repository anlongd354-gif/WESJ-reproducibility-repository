# ArcGIS Workflow 05: Spatial Autocorrelation

## Inputs

Annual county polygons joined to finite county-level WESJ values by `unit_id`.

## Parameters

Queen contiguity and row standardization at baseline; Rook and KNN-4 for
robustness; Euclidean distance; 999 Local Moran permutations; and `NO_FDR`.

## Outputs

Global Moran's I summary tables and annual LISA feature classes containing
`LMiIndex`, `LMiZScore`, `LMiPValue`, `COType`, and `NNeighbors`.

## Manuscript and SI Correspondence

Manuscript Section 2.1 describes the spatial-analysis role; results and
interpretation are in Section 4.4.2. Detailed parameter and spatial-weight
robustness records are in Text S8 and Tables S5-S9. The reported analysis was
performed with ArcGIS Pro GUI tools. The ArcPy file is only an example record.

## Input Preparation

Join annual county-level WESJ values to the administrative polygons by
`unit_id`. Select records with finite WESJ values.

## Global Moran's I

Tool: **Spatial Statistics Tools > Analyzing Patterns > Spatial
Autocorrelation (Moran's I)**

| Parameter | Baseline setting |
|---|---|
| Input Feature Class | Annual polygon layer with WESJ |
| Input Field | WESJ |
| Generate Report | NO_REPORT or GENERATE_REPORT, recorded consistently |
| Conceptualization | CONTIGUITY_EDGES_CORNERS |
| Distance Method | EUCLIDEAN_DISTANCE |
| Standardization | ROW |

Record Moran's I, z score, p value, sample size, year, and spatial-weight
definition.

## LISA

Tool: **Spatial Statistics Tools > Mapping Clusters > Cluster and Outlier
Analysis (Anselin Local Moran's I)**

| Parameter | Baseline setting |
|---|---|
| Input Feature Class | Annual polygon layer with WESJ |
| Input Field | WESJ |
| Conceptualization | CONTIGUITY_EDGES_CORNERS |
| Distance Method | EUCLIDEAN_DISTANCE |
| Standardization | ROW |
| Apply FDR Correction | NO_FDR |
| Number of Permutations | 999 |

Retain ArcGIS output fields including `LMiIndex`, `LMiZScore`, `LMiPValue`,
`COType`, and `NNeighbors`.

## Spatial-Weight Sensitivity

Repeat both tools with:

```text
CONTIGUITY_EDGES_ONLY
K_NEAREST_NEIGHBORS, number_of_neighbors = 4
```

Classification sensitivity is separate from spatial-weight sensitivity.
Neither classification nor LISA categories should be used to calculate
continuous WESJ deficit contributions.

## Notes

- Polygon contiguity requires valid polygon topology.
- A projected CRS is recommended for distance-based specifications.
- Keep the feature order and `unit_id` stable across years.
- ArcGIS warnings about islands or features with no neighbors must be retained
  in the local processing log.
