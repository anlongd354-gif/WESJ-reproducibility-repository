# Author Release Checklist

- [ ] `config/paths_local.yaml` is absent from the public repository.
- [ ] `data/`, `outputs/`, `scratch/`, and `logs/` are absent.
- [ ] No raster, vector, spreadsheet, database, or result table is committed.
- [ ] No real administrative-unit names or codes remain.
- [ ] No local drive paths, usernames, email addresses, or account identifiers remain.
- [ ] `metadata/input_data_inventory_template.csv` contains metadata only, not observations.
- [ ] The exact software environment has been recorded.
- [ ] ArcGIS tool names, environment settings, Raster Calculator expressions, and warnings have been checked against the final run.
- [ ] Every parameter used in the manuscript is represented in the configuration.
- [ ] `python scripts/99_sanitize_audit.py` passes.
- [ ] A clean-machine test has been completed using authorized local inputs.
- [ ] Repository DOI and release version have been added to the manuscript only after deposit.
