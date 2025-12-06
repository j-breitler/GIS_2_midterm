'''
This script creates a region mask for the study area.

The region mask is NOT primarily used for clipping other layers. Instead, it serves as:
The starting point - A raster where ALL pixels = 1 (available)
The canvas for exclusions - Each exclusion constraint will turn pixels from 1 → 0
The final eligibility map - After all exclusions, remaining 1s = eligible land
'''

import sys
from pathlib import Path

# ============================================
# SETUP: Add project root to Python path
# ============================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================
# IMPORTS FROM CONFIG
# ============================================
from config import (
    STUDY_AREA_SHAPEFILE,  # Input: study area boundary
    REGION_MASK,           # Output: region mask raster
    TARGET_CRS,            # Target coordinate system (EPSG:32633)
    RESOLUTION,            # Raster resolution in meters (100)
    PREPROCESSED_DIR,      # Output directory
)

# ============================================
# OTHER IMPORTS
# ============================================
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
import geopandas as gpd
import numpy as np
from pyproj import CRS

# Create output directory if needed
PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# LOAD AND VALIDATE CRS
# ============================================
print("Loading boundary shapefile...")
boundary = gpd.read_file(STUDY_AREA_SHAPEFILE)

# Check if Layer has a CRS
if boundary.crs is None:
    raise ValueError(
        f"Shapefile '{STUDY_AREA_SHAPEFILE}' has no CRS! "
        "Please define CRS (e.g. in QGIS) before proceeding."
    )

# Create CRS objects for robust comparison
''' 
    String comparison can fail if CRS is defined differently
    but means the same thing. Object comparison recognizes
    equivalent CRS definitions 
'''

input_crs = CRS.from_user_input(boundary.crs)
target_crs = CRS.from_user_input(TARGET_CRS)

if not input_crs.equals(target_crs):
    print(f"Reprojecting from {input_crs.to_string()} to {target_crs.to_string()}...")
    boundary = boundary.to_crs(target_crs)
    print("Reprojection complete")
else:
    print(f"CRS is correct: {target_crs.to_string()}")

# ============================================
# CREATE REGION MASK
# ============================================
print("Creating region mask...")

# Get bounds
'''.total_bounds is a GeoPandas property that returns the bounding box of ALL 
    geometries in the GeoDataFrame. The raster we want to create needs to know its
    geographic extent - where in the world it sits. The bounds define the corners of
    your raster in coordinate space. We get this extent from our study area vector layer. 
'''

bounds = boundary.total_bounds  # (minx, miny, maxx, maxy)

# Calculate dimensions
'''
    Rasters are matrices of pixels - we need to know the dimensions (rows × columns).
    The raster must have enough pixels to cover your entire study area at 100m resolution
    width = number of columns
    height = number of rows
'''
width = int(np.ceil((bounds[2] - bounds[0]) / RESOLUTION))
height = int(np.ceil((bounds[3] - bounds[1]) / RESOLUTION))

print(f"Raster dimensions: {width} x {height} pixels")
print(f"Pixel size: {RESOLUTION} x {RESOLUTION} meters")

# Create transform
'''
    A transform (specifically an "affine transform") is a mathematical 
    mapping that connects:
    Pixel coordinates (row, column in the array) ↔ 
    Geographic coordinates (meters/degrees on Earth)
    Think of it as the **GPS metadata** for your raster.
    Without a transform, your raster is just a matrix of 
    numbers with no geographic context
'''
transform = from_bounds(bounds[0], bounds[1], bounds[2], bounds[3], 
                        width, height)

# Rasterize
'''
    The rasterize function turns your vector data into a raster.
    It converts each polygon in your vector layer into a grid of pixels,
    where each pixel is either 1 (inside the polygon) or 0 (outside the polygon).
'''
mask = rasterize(
    [(geom, 1) for geom in boundary.geometry],
    out_shape=(height, width),
    transform=transform,
    fill=0,  # Background value (outside study area)
    dtype='uint8'
)

# Save with proper CRS
'''
This saves the NumPy array as a GeoTIFF file with proper metadata
'''
print(f"Saving to {REGION_MASK}...")
with rasterio.open(
    REGION_MASK,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='uint8',
    crs=target_crs,  # Use the target CRS
    transform=transform,
    nodata=0,
    compress='lzw'  # Add compression to reduce file size
) as dst:
    dst.write(mask, 1)

print(f"Region mask created successfully!")
print(f"  - Total pixels: {width * height:,}")
print(f"  - Study area pixels: {np.sum(mask == 1):,}")
print(f"  - Study area: {np.sum(mask == 1) * RESOLUTION * RESOLUTION / 1e6:.2f} km2")
