"""
Create slope exclusion from DEM

This script:
1. Loads the clipped DEM (output from reproject_clip_dem.py)
2. Resamples to match region mask if needed
3. Calculates slope in degrees
4. Creates exclusion raster where slope > MAX_SLOPE_DEGREES

Input:  DEM_clipped.tif from PREPROCESSED_DIR
Output: slope_exclusion.tif in PREPROCESSED_DIR/exclusions/
"""

import sys
import os
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
    PREPROCESSED_DIR,      # Base directory for processed files
    REGION_MASK,           # Template raster for dimensions/CRS
    MAX_SLOPE_DEGREES,     # Slope threshold for exclusion
)

# ============================================
# OTHER IMPORTS
# ============================================
import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
from scipy.ndimage import sobel

# ============================================
# INPUT/OUTPUT PATHS
# ============================================
# Input: clipped DEM from reproject_clip_dem.py
DEM_CLIPPED = PREPROCESSED_DIR / "DEM_clipped.tif"

# Output directory
EXCLUSIONS_DIR = PREPROCESSED_DIR / "exclusions"

# Output files
SLOPE_OUTPUT = EXCLUSIONS_DIR / "slope.tif"
SLOPE_EXCLUSION_OUTPUT = EXCLUSIONS_DIR / "slope_exclusion.tif"

# Create output directory
EXCLUSIONS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("SLOPE EXCLUSION")
print("=" * 60)
print(f"DEM input:       {DEM_CLIPPED}")
print(f"Region mask:     {REGION_MASK}")
print(f"Slope threshold: {MAX_SLOPE_DEGREES} degrees")
print()

# ============================================
# STEP 1: LOAD REGION MASK (TARGET TEMPLATE)
# ============================================
print("[1/5] Loading region mask (target template)...")

with rasterio.open(REGION_MASK) as src:
    region_mask = src.read(1)
    target_meta = src.meta.copy()
    target_transform = src.transform
    target_crs = src.crs
    target_shape = (src.height, src.width)

print(f"  Target dimensions: {target_shape[1]} x {target_shape[0]} pixels")
print(f"  Target resolution: {target_transform.a}m")

# ============================================
# STEP 2: LOAD AND RESAMPLE DEM
# ============================================
print("\n[2/5] Loading DEM...")

with rasterio.open(DEM_CLIPPED) as src:
    dem_data = src.read(1)
    dem_meta = src.meta.copy()
    dem_transform = src.transform
    dem_crs = src.crs
    dem_shape = (src.height, src.width)

print(f"  DEM dimensions: {dem_shape[1]} x {dem_shape[0]} pixels")

# Check if resampling needed
needs_resampling = dem_shape != target_shape

if needs_resampling:
    print("\n[3/5] Resampling DEM to match region mask...")
    
    # Create empty array with target dimensions
    elevation = np.empty(target_shape, dtype=np.float32)
    
    # Reproject/resample DEM to match region mask
    reproject(
        source=dem_data,
        destination=elevation,
        src_transform=dem_transform,
        src_crs=dem_crs,
        dst_transform=target_transform,
        dst_crs=target_crs,
        resampling=Resampling.bilinear
    )
    
    print(f"  Resampled to: {elevation.shape[1]} x {elevation.shape[0]} pixels")
    transform = target_transform
else:
    print("\n[3/5] DEM matches region mask, no resampling needed")
    elevation = dem_data
    transform = dem_transform

print(f"  Elevation range: {elevation.min():.1f}m to {elevation.max():.1f}m")

# ============================================
# STEP 3: CALCULATE SLOPE
# ============================================
print("\n[4/5] Calculating slope...")

# Get pixel size
pixel_size_x = transform.a
pixel_size_y = -transform.e

# Calculate gradients using Sobel operator
dx = sobel(elevation, axis=1) / (8 * pixel_size_x)
dy = sobel(elevation, axis=0) / (8 * pixel_size_y)

# Calculate slope angle in degrees
slope_radians = np.arctan(np.sqrt(dx**2 + dy**2))
slope_degrees = np.degrees(slope_radians)

print(f"  Slope range: {slope_degrees.min():.1f} to {slope_degrees.max():.1f} degrees")

# Save slope raster
slope_meta = target_meta.copy()
slope_meta.update({'dtype': 'float32', 'compress': 'lzw'})

with rasterio.open(SLOPE_OUTPUT, 'w', **slope_meta) as dst:
    dst.write(slope_degrees.astype('float32'), 1)

print(f"  [OK] Slope raster saved to {SLOPE_OUTPUT.name}")

# ============================================
# STEP 4: CREATE SLOPE EXCLUSION
# ============================================
print("\n[5/5] Creating slope exclusion...")

# Create exclusion: 1 = slope too steep (exclude), 0 = acceptable
slope_exclusion_raw = (slope_degrees > MAX_SLOPE_DEGREES).astype('uint8')

# Apply region mask (only count pixels inside study area)
slope_exclusion = slope_exclusion_raw & region_mask

# Calculate statistics
total_pixels = np.sum(region_mask == 1)
excluded_pixels = np.sum(slope_exclusion == 1)
excluded_percent = (excluded_pixels / total_pixels) * 100 if total_pixels > 0 else 0
pixel_area = pixel_size_x * pixel_size_y
excluded_area_km2 = (excluded_pixels * pixel_area) / 1e6

print(f"  Excluded pixels: {excluded_pixels:,} / {total_pixels:,} ({excluded_percent:.2f}%)")
print(f"  Excluded area: {excluded_area_km2:.2f} km2")

# Save exclusion raster
exclusion_meta = target_meta.copy()
exclusion_meta.update({'dtype': 'uint8', 'nodata': None, 'compress': 'lzw'})

with rasterio.open(SLOPE_EXCLUSION_OUTPUT, 'w', **exclusion_meta) as dst:
    dst.write(slope_exclusion, 1)

file_size_kb = os.path.getsize(SLOPE_EXCLUSION_OUTPUT) / 1024
print(f"  [OK] Slope exclusion saved to {SLOPE_EXCLUSION_OUTPUT.name} ({file_size_kb:.1f} KB)")

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("SLOPE EXCLUSION COMPLETE")
print("=" * 60)
print(f"Threshold: > {MAX_SLOPE_DEGREES} degrees")
print(f"Excluded:  {excluded_area_km2:.2f} km2 ({excluded_percent:.2f}%)")
print(f"Output:    {EXCLUSIONS_DIR}")
print("=" * 60)
