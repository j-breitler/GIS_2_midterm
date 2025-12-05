'''
This script creates a region mask for the study area.
It is used to mask the raster data to the study area.

Data Import needs to been improved to be more robust.
For now you need to manually define the input and output paths.
'''

import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import numpy as np
from pyproj import CRS

# ============================================
# CONFIGURATION
# ============================================
TARGET_CRS = "EPSG:32633"  # WGS 84 / UTM zone 33N
RESOLUTION = 100  # meters
INPUT_SHAPEFILE = r'C:/Studium/MASTER/KURSE/GIS_Analysetechniken_2/GIS_2_midterm/data/raw/BezirkundNatura2000/Suedoststeiermark_Shapefile.shp'
OUTPUT_RASTER = r'C:/Studium/MASTER/KURSE/GIS_Analysetechniken_2/GIS_2_midterm/data/preprocessed/region_mask_100m.tif'

# ============================================
# LOAD AND VALIDATE CRS
# ============================================
print("Loading boundary shapefile...")
boundary = gpd.read_file(INPUT_SHAPEFILE)

# Check if Layer has a CRS
if boundary.crs is None:
    raise ValueError(
        f"Shapefile '{INPUT_SHAPEFILE}' has no CRS! "
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
    print(f"⚠ Reprojecting from {input_crs.to_string()} to {target_crs.to_string()}...")
    boundary = boundary.to_crs(target_crs)
    print("✓ Reprojection complete")
else:
    print(f"✓ CRS is correct: {target_crs.to_string()}")

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
from rasterio.transform import from_bounds
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
print(f"Saving to {OUTPUT_RASTER}...")
with rasterio.open(
    OUTPUT_RASTER,
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

print(f"✓ Region mask created successfully!")
print(f"  - Total pixels: {width * height:,}")
print(f"  - Study area pixels: {np.sum(mask == 1):,}")
print(f"  - Study area: {np.sum(mask == 1) * RESOLUTION * RESOLUTION / 1e6:.2f} km²")