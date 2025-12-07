# Results Folder Structure

This folder contains all outputs from the Austria PV potential assessment analysis.

## Folder Organization

### `rasters/`
Geospatial raster data outputs from analysis processes:
- Slope rasters
- Land eligibility masks
- Solar potential maps
- LCOE (Levelized Cost of Electricity) rasters
- Exclusion criteria layers

### `vectors/`
Vector data outputs:
- Processed shapefiles
- Eligible area polygons
- Analysis boundaries
- Regional summaries

### `figures/`
Visualization outputs:
- Maps and charts
- PNG/JPG images
- Plot outputs
- Presentation graphics

### `reports/`
Text and document outputs:
- Analysis reports
- Statistical summaries
- Methodology documentation
- Regional assessments

### `temp/`
Temporary files and intermediate results:
- Processing artifacts
- Debug outputs
- Cache files
- Files that can be deleted after final analysis

## File Naming Convention

Files should follow this naming pattern:
`{analysis_type}_{region}_{date}_{version}.{extension}`

Examples:
- `slope_suedoststeiermark_20241204_v1.tif`
- `land_eligibility_at22_20241204_v1.shp`
- `lcoe_austria_national_20241204_v1.png`
- `capacity_potential_at11_20241204_report.pdf`

## Data Formats

- **Rasters**: GeoTIFF (.tif)
- **Vectors**: Shapefile (.shp, .dbf, .prj, .shx)
- **Figures**: PNG (.png), PDF (.pdf)
- **Reports**: Markdown (.md), PDF (.pdf), Excel (.xlsx)



