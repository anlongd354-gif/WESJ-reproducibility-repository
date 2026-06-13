# Data Policy

This repository contains no original data, derived rasters, administrative
records, study results, or machine-specific paths. The authors do not have
permission to share the restricted source datasets.

All files under `data/`, `outputs/`, `scratch/`, and `logs/` are excluded from
version control. Readers must obtain restricted datasets independently from
their original providers under the applicable access conditions and place them
locally according to `config/paths_local.yaml`.

The presence of metadata, filename, and path templates does not mean that any
source dataset is publicly available or redistributable by the authors.

The public repository should contain only:

- source code;
- an example configuration with generic placeholders;
- software dependency files;
- metadata templates;
- calculation and reconstruction instructions.

Before public release, run `scripts/99_sanitize_audit.py` and inspect its report.
