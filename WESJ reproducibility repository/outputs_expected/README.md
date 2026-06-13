# Expected Outputs

The repository does not include numerical results. After authorized users
prepare the required inputs, the workflow creates:

| Directory | Main outputs |
|---|---|
| `outputs/wdei/` | Local Gini-based WDEI rasters |
| `outputs/wuei/` | DEA-BCC WUEI rasters |
| `outputs/wesj/` | Baseline WESJ rasters and parameter JSON files |
| `outputs/sensitivity/wsi/` | WSI scenario rasters and summary table |
| `outputs/sensitivity/classification/` | Classification breaks and low-WESJ membership tables |
| `outputs/deficit_attribution/` | M1-M7 WESJ and component-deficit contribution outputs |
| `outputs/summary_tables/` | Combined county-year and robustness summaries |

Classification outputs are used only to identify low-WESJ units. Continuous
WESJ values and continuous contribution values remain the basis for deficit
attribution.
