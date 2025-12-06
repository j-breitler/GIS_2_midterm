'''
This script rasterizes the vector data into a raster.

'''

import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import numpy as np
from pyproj import CRS

# ============================================
# HARDCODED PARAMETERS (change these for your test)
# ============================================

# Path to your region mask (template)
REGION_MASK_PATH = "C:/Studium/MASTER/KURSE/GIS_Analysetechniken_2/GIS_2_midterm/data/preprocessed/region_mask_100m.tif"

# Path to input vector file
INPUT_VECTOR_PATH = "C:/Studium/MASTER/KURSE/GIS_Analysetechniken_2/GIS_2_midterm/data/raw/OSM_DATA/Strassen_Steiermark.shp"

# Path to output raster
OUTPUT_RASTER_PATH = "C:/Studium/MASTER/KURSE/GIS_Analysetechniken_2/GIS_2_midterm/data/preprocessed/roads_exclusion.tif"

# Expected CRS (should match region mask)
TARGET_CRS = "EPSG:32633"


# ============================================
# STEP 1: LOAD REGION MASK METADATA
# ============================================
print("="*60)
print("VECTOR TO RASTER CONVERSION (SIMPLE VERSION)")
print("="*60)

print("\n[Step 1/5] Loading region mask metadata...")

# Load Region Mask Metadata
'''
We need the template from the region mask to create the exclusion rasters.
Gets: dimensions, resolution, CRS, transform
All exclusion rasters MUST match this template

What we extract:
meta: Dictionary with all raster properties
transform: Affine transform (pixel ↔ coordinate mapping)
region_crs: Coordinate reference system
'''

with rasterio.open(REGION_MASK_PATH) as src:
    meta = src.meta.copy()
    transform = src.transform
    region_crs = src.crs
    
    print(f"  Template file: {REGION_MASK_PATH}")
    print(f"  Dimensions: {meta['width']} x {meta['height']} pixels")
    print(f"  Resolution: {transform.a} m x {-transform.e} m")
    print(f"  CRS: {region_crs}")


# ============================================
# STEP 2: LOAD VECTOR DATA
# ============================================
print(f"\n[Step 2/5] Loading vector data...")

gdf = gpd.read_file(INPUT_VECTOR_PATH)

print(f"  Input file: {INPUT_VECTOR_PATH}")
print(f"  Features loaded: {len(gdf)}")
print(f"  Geometry types: {gdf.geom_type.unique().tolist()}")
print(f"  Input CRS: {gdf.crs}")


# ============================================
# STEP 3: VALIDATE AND REPROJECT CRS
# ============================================
print(f"\n[Step 3/5] Validating CRS...")

# Check if CRS is defined
if gdf.crs is None:
    raise ValueError(
        "ERROR: Input vector file has no CRS defined!\n"
        "Please set CRS in QGIS:\n"
        "  1. Right-click layer → Properties → Source\n"
        "  2. Click 'Select CRS' button\n"
        "  3. Choose the correct CRS\n"
        "  4. Save the layer"
    )

# Compare CRS
'''
For explaination take a look at the raster_region_mask.py file.
'''

input_crs = CRS.from_user_input(gdf.crs)
target_crs = CRS.from_user_input(TARGET_CRS)

if not input_crs.equals(target_crs):
    print(f"  ⚠ CRS mismatch detected!")
    print(f"    Input CRS:  {input_crs.to_string()}")
    print(f"    Target CRS: {target_crs.to_string()}")
    print(f"  Reprojecting...")
    
    gdf = gdf.to_crs(target_crs)
    
    print(f"  ✓ Reprojection complete")
else:
    print(f"  ✓ CRS matches: {target_crs.to_string()}")


# ============================================
# STEP 4: RASTERIZE
# ============================================
print(f"\n[Step 4/5] Rasterizing...")

# Create list of (geometry, value) pairs
# Value 1 = exclude this area
# Value 0 = available (background)
shapes = [(geom, 1) for geom in gdf.geometry]

print(f"  Rasterizing {len(shapes)} features...")
print(f"  Output shape: {meta['height']} rows x {meta['width']} columns")

# Perform rasterization
exclusion = rasterize(
    shapes=shapes,                            # Geometries to rasterize
    out_shape=(meta['height'], meta['width']), # Match region mask dimensions
    transform=transform,                       # Use region mask transform
    fill=0,                                    # Background value (available)
    dtype='uint8',                            # Data type
    all_touched=False                         # Only pixels whose CENTER is inside geometry
)

# Calculate statistics
excluded_pixels = np.sum(exclusion == 1) # creates Boolean array
available_pixels = np.sum(exclusion == 0) # creates Boolean array
total_pixels = exclusion.size
excluded_percent = (excluded_pixels / total_pixels) * 100 # Calculate percentage

# Calculate area (assuming 100m resolution)
pixel_area_m2 = transform.a * (-transform.e)  # width * height in meters
excluded_area_km2 = (excluded_pixels * pixel_area_m2) / 1e6 # Pixels × area per pixel = total excluded area in m². Divide by 1,000,000 to convert m² → km²

print(f"  ✓ Rasterization complete")
print(f"\n  Statistics:")
print(f"    Total pixels:      {total_pixels:,}")
print(f"    Excluded pixels:   {excluded_pixels:,} ({excluded_percent:.2f}%)")
print(f"    Available pixels:  {available_pixels:,} ({100-excluded_percent:.2f}%)")
print(f"    Excluded area:     {excluded_area_km2:.2f} km²")


# ============================================
# STEP 5: SAVE OUTPUT
# ============================================
print(f"\n[Step 5/5] Saving output...")

# Update metadata for output file
meta.update({
    'dtype': 'uint8',
    'nodata': None,      # All pixels are valid (0 or 1)
    'compress': 'lzw'    # Compress to reduce file size
})

# Save raster
with rasterio.open(OUTPUT_RASTER_PATH, 'w', **meta) as dst:
    dst.write(exclusion, 1)  # Write to band 1

print(f"  ✓ Output saved: {OUTPUT_RASTER_PATH}")

# Check file size
import os
file_size_kb = os.path.getsize(OUTPUT_RASTER_PATH) / 1024
print(f"  ✓ File size: {file_size_kb:.2f} KB")


# ============================================
# SUMMARY
# ============================================
print("\n" + "="*60)
print("CONVERSION COMPLETE!")
print("="*60)
print(f"\nInput:  {INPUT_VECTOR_PATH}")
print(f"Output: {OUTPUT_RASTER_PATH}")
print(f"\nExcluded: {excluded_area_km2:.2f} km² ({excluded_percent:.2f}%)")
print("="*60)