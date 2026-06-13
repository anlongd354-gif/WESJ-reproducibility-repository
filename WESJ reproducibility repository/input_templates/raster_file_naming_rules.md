# Raster File Naming Rules

Use lowercase ASCII names and a four-digit year:

```text
{variable}_{year}.tif
```

Examples use placeholders only:

```text
population_YYYY.tif
wsi_normalized_YYYY.tif
wdei_YYYY.tif
wuei_YYYY.tif
```

Rules:

1. Keep one variable and one year per single-band raster.
2. Store units and scaling factors in `metadata/input_data_metadata.csv`.
3. Use the same CRS, cell size, extent, cell origin, and NoData mask after
   preprocessing.
4. Do not encode administrative names, provider account names, or restricted
   dataset identifiers in public filenames.
5. Put all private inputs under an ignored local directory and record their
   paths only in `config/paths_local.yaml`.
