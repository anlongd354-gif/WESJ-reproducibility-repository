from __future__ import annotations

"""Validate the private inputs required by the reconstruction workflow.

Inputs: `config/paths_local.yaml`, reference raster, boundaries, and annual
source rasters.
Parameters: study years and generic path patterns in the local configuration.
Outputs: console validation report; no analytical data product.
Paper/SI: infrastructure supporting manuscript Sections 2.1-2.3 and Texts
S1-S9; included to address computational transparency.
"""

from common import format_path, load_settings, resolve_path, years_from_paths


def main() -> None:
    paths, _ = load_settings()
    years = years_from_paths(paths)
    missing = []

    reference = resolve_path(paths["inputs"]["reference_raster"])
    boundaries = resolve_path(paths["inputs"]["administrative_boundaries"])
    for required in (reference, boundaries):
        if not required.exists():
            missing.append(required)

    raster_patterns = paths["inputs"]["rasters"]
    for year in years:
        for pattern in raster_patterns.values():
            candidate = format_path(pattern, year=year)
            if not candidate.exists():
                missing.append(candidate)

    if missing:
        details = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(f"Missing private inputs:\n{details}")
    print(f"Validated required inputs for {len(years)} year(s).")


if __name__ == "__main__":
    main()
