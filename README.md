# GIS-based Assessment of Utility-Scale Photovoltaic Potential in Suedoststeiermark, Austria

This project adapts and implements the methodology from "A GIS-based method for assessing the economics of utility-scale photovoltaic systems" (Benalcazar et al., 2024) to assess solar photovoltaic potential in Suedoststeiermark, a district in the Austrian state of Styria.

## Project Overview

### Original Methodology
The original study developed a comprehensive GIS-based framework to assess land eligibility and techno-economic potential of utility-scale photovoltaic (PV) systems in Poland. The approach combines:
- **Land eligibility analysis** using exclusion criteria to identify suitable areas
- **Techno-economic assessment** using Levelized Cost of Electricity (LCOE) calculations
- **Spatial analysis** at 100m resolution across administrative regions

### Adaptation for Suedoststeiermark
We adapt this methodology to the Suedoststeiermark district context, focusing on a smaller-scale, detailed analysis suitable for regional planning and decision-making.

---

## Quick Start: Running the Analysis

### Prerequisites
1. Install Python dependencies: pip install -r requirements.txt
2. Place raw data in data/raw/ (see Data Sources section)
3. Run python config.py to verify setup and create directories

### Script Execution Order

**IMPORTANT: Run the preprocessing scripts in this exact order:**

| Step | Script | Output |
|------|--------|--------|
| 1 | python scripts/preprocessing/raster_region_mask.py | data/preprocessed/region_mask_100m.tif |
| 2 | python scripts/preprocessing/reproject_clip_dem.py | data/preprocessed/DEM_clipped.tif |
| 3 | python scripts/preprocessing/reproject_clip_shps.py | data/preprocessed/clipped/*_clipped.shp |
| 4 | python scripts/preprocessing/buffer_shps.py | data/preprocessed/buffered/*_buffered.shp |
| 5 | python scripts/preprocessing/slope_exclusion.py | data/preprocessed/exclusions/slope_exclusion.tif |
| 6 | python scripts/preprocessing/batch_process_vector_to_raster_exclusion.py | data/preprocessed/exclusions/*_exclusion.tif |
| 7 | python scripts/preprocessing/master_exclusion.py | data/preprocessed/master_suitability.tif **(FINAL)** |

### Data Flow Diagram

Study Area Shapefile --> region_mask_100m.tif --+
                                                |
DEM (30m) --> DEM_clipped.tif --> slope_exclusion.tif --+
                                                         |
Vector Shapefiles:                                       |
  Airport, Forest, Industry,    clipped/    buffered/    |
  Natura2000, Powerlines,   --> *_clipped --> *_buffered --> exclusions/ --+--> master_suitability.tif
  Railway, Streets,                                      |     (1=suitable, 0=excluded)
  UrbanArea, WaterBodies                     ------------+

---

## Project Structure

GIS_2_midterm/
|-- config.py                    # Central configuration (paths, settings, parameters)
|-- requirements.txt             # Python dependencies
|-- README.md                    # This file
|
|-- data/
|   |-- raw/                     # Original unmodified input data
|   |   |-- Raster/DEM/          # Digital Elevation Model
|   |   |-- Raster/PVOUT.tif     # Solar PV output potential
|   |   |-- Vector/              # Constraint shapefiles (9 files)
|   |   +-- Study_Area_Vector/   # Suedoststeiermark boundary
|   |
|   |-- preprocessed/            # Intermediate processing outputs
|   |   |-- region_mask_100m.tif # Study area raster mask
|   |   |-- DEM_clipped.tif      # Clipped DEM
|   |   |-- master_suitability.tif # FINAL combined suitability
|   |   |-- clipped/             # Reprojected and clipped vectors
|   |   |-- buffered/            # Buffered vectors
|   |   +-- exclusions/          # Individual exclusion rasters
|   |
|   |-- processed/               # Fully processed data
|   +-- results/                 # Final outputs (figures, rasters, vectors, reports)
|
|-- scripts/
|   |-- preprocessing/           # Steps 1-7 (see execution order above)
|   |-- analysis/                # Analysis/calculation scripts
|   +-- visualisation/           # Plotting/mapping scripts
|
|-- docs/                        # Documentation
+-- notebooks/                   # Jupyter notebooks

---

## Configuration System

All paths and parameters are centralized in config.py.

### Key Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| TARGET_CRS | EPSG:32633 | UTM Zone 33N (meters) |
| RESOLUTION | 100m | Raster pixel size |
| MAX_SLOPE_DEGREES | 15 degrees | Slope threshold for exclusion |

### Buffer Distances

| Constraint | Buffer (m) | Rationale |
|------------|------------|-----------|
| Powerlines | 120 | Safety distance |
| Streets | 100 | Road setback |
| Railway | 100 | Railway setback |
| Airport | 5000 | Flight paths, noise |
| Urban Area | 500 | Residential buffer |
| Industry | 500 | Industrial zone buffer |
| Water Bodies | 0 | Direct exclusion only |
| Natura 2000 | 300 | Protected area buffer |
| Forest | 0 | Direct exclusion only |

### Using config.py in Scripts

# Add project root to path
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import RAW_VECTORS, STUDY_AREA_SHAPEFILE, PREPROCESSED_DIR, TARGET_CRS

---

## Preprocessing Scripts Detail

### Step 1: raster_region_mask.py
Creates binary raster mask (1=inside, 0=outside) at 100m resolution as template.

### Step 2: reproject_clip_dem.py
Reprojects raw DEM to UTM 33N and clips to study area (in-memory processing).

### Step 3: reproject_clip_shps.py
Reprojects all constraint shapefiles to UTM 33N and clips. Output: preprocessed/clipped/

### Step 4: buffer_shps.py
Applies buffer distances from config.BUFFER_DISTANCES. Output: preprocessed/buffered/

### Step 5: slope_exclusion.py
Calculates slope using Sobel operator. Creates exclusion where slope > 15 degrees.

### Step 6: batch_process_vector_to_raster_exclusion.py
Converts buffered shapefiles to rasters matching region mask. Output: exclusions/

### Step 7: master_exclusion.py
Combines all exclusions: suitability = region_mask AND (NOT each_exclusion)
Output: master_suitability.tif (1=suitable, 0=excluded)

---

## Analysis Results

- **Study Area**: ~987 km2
- **Suitable Area**: ~106 km2 (10.74%)
- **Excluded Area**: ~881 km2 (89.26%)

---

## Data Sources

### Vector Data
- OpenStreetMap (OSM): Roads, railways, airports, urban areas, forests (Geofabrik.de)
- Protected Areas: Natura 2000 sites (Austrian Federal Environment Agency)
- Administrative Boundaries: data.gv.at

### Raster Data
- DEM: SRTM 30m (NASA, https://doi.org/10.5069/G9445JDF)
- PVOUT: Solar PV output potential (kWh/kWp/year)

---

## Key Python Libraries

- geopandas: Vector geospatial processing
- rasterio: Raster I/O and processing
- shapely: Geometric operations
- pyproj: CRS transformations
- numpy: Array operations
- scipy: Slope calculations (Sobel operator)
- matplotlib: Visualization

---

## Troubleshooting

### PROJ Library Conflict
If you see PROJ database errors, config.py includes a fix that sets PROJ_LIB correctly.
Common when PostGIS or QGIS is installed.

### Missing .shx Files
Scripts set SHAPE_RESTORE_SHX=YES to handle shapefiles with missing .shx files.

---

## References

1. Benalcazar, P., Komorowska, A., and Kaminski, J. (2024). A GIS-based method for assessing the economics of utility-scale photovoltaic systems. Applied Energy, 353, 122044.

2. IRENA. (2022). Renewable power generation costs in 2021.

3. European Commission. (2022). EU solar energy strategy.
