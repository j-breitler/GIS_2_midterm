"""
Batch process vector files to create exclusion rasters

This script:
1. Loads the region mask as template (gets extent, resolution, CRS)
2. Reads buffered shapefiles (output from buffer_shps.py)
3. Rasterizes each to create exclusion rasters matching the region mask

Input:  Buffered shapefiles from PREPROCESSED_DIR/buffered/
Output: Exclusion rasters (1 = exclude, 0 = available) in PREPROCESSED_DIR/exclusions/
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
    REGION_MASK,           # Template raster for dimensions/CRS
    PREPROCESSED_DIR,      # Base directory for processed files
    TARGET_CRS,            # Target coordinate system
    BUFFER_DISTANCES,      # Dictionary of constraint names (used as keys)
)

# ============================================
# OTHER IMPORTS
# ============================================
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import numpy as np
from pyproj import CRS

# ============================================
# INPUT/OUTPUT DIRECTORIES
# ============================================
# Input: buffered shapefiles from buffer_shps.py
BUFFERED_DIR = PREPROCESSED_DIR / "buffered"

# Output: exclusion rasters
EXCLUSIONS_DIR = PREPROCESSED_DIR / "exclusions"

# ============================================
# LOAD REGION MASK METADATA (TEMPLATE)
# ============================================
'''
We need the template from the region mask to create the exclusion rasters.
Gets: dimensions, resolution, CRS, transform
All exclusion rasters MUST match this template
'''

print("=" * 60)
print("BATCH VECTOR TO RASTER CONVERSION")
print("=" * 60)
print(f"\nInput dir:  {BUFFERED_DIR}")
print(f"Output dir: {EXCLUSIONS_DIR}")
print(f"Template:   {REGION_MASK}")

# Create output directory
EXCLUSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Load template metadata from region mask
with rasterio.open(REGION_MASK) as src:
    meta = src.meta.copy()
    transform = src.transform
    region_crs = src.crs

print(f"\nTemplate dimensions: {meta['width']} x {meta['height']} pixels")
print(f"Template CRS: {region_crs}")
print(f"\nConstraints to process: {len(BUFFER_DISTANCES)}")

# ============================================
# PROCESS EACH EXCLUSION
# ============================================

successful = 0
failed = 0
skipped = 0

for name in BUFFER_DISTANCES.keys():
    print(f"\n{'-' * 60}")
    print(f"Processing: {name}")
    print(f"{'-' * 60}")
    
    # Input file from buffered directory
    input_path = BUFFERED_DIR / f"{name}_buffered.shp"
    output_path = EXCLUSIONS_DIR / f"{name}_exclusion.tif"
    
    print(f"Input:  {input_path.name}")
    print(f"Output: {output_path.name}")
    
    try:
        # Check if input file exists
        if not input_path.exists():
            print(f"  [SKIP] Input file not found")
            skipped += 1
            continue
        
        # Load vector data
        gdf = gpd.read_file(input_path)
        print(f"  Features loaded: {len(gdf)}")
        
        # Check CRS
        if gdf.crs is None:
            print(f"  [FAIL] No CRS defined")
            failed += 1
            continue
        
        # Reproject if needed
        input_crs = CRS.from_user_input(gdf.crs)
        target_crs = CRS.from_user_input(TARGET_CRS)
        
        if not input_crs.equals(target_crs):
            print(f"  Reprojecting to {TARGET_CRS}...")
            gdf = gdf.to_crs(target_crs)
        
        # Rasterize
        print(f"  Rasterizing...")
        shapes = [(geom, 1) for geom in gdf.geometry]
        
        exclusion_raster = rasterize(
            shapes=shapes,
            out_shape=(meta['height'], meta['width']),
            transform=transform,
            fill=0,
            dtype='uint8',
            all_touched=False
        )
        
        # Calculate statistics
        excluded_pixels = np.sum(exclusion_raster == 1)
        excluded_percent = (excluded_pixels / exclusion_raster.size) * 100
        pixel_area = transform.a * (-transform.e)
        excluded_area_km2 = (excluded_pixels * pixel_area) / 1e6
        
        print(f"  Excluded pixels: {excluded_pixels:,} ({excluded_percent:.2f}%)")
        print(f"  Excluded area: {excluded_area_km2:.2f} km2")
        
        # Save
        output_meta = meta.copy()
        output_meta.update({'dtype': 'uint8', 'nodata': None, 'compress': 'lzw'})
        
        with rasterio.open(output_path, 'w', **output_meta) as dst:
            dst.write(exclusion_raster, 1)
        
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"  [OK] Saved ({file_size_kb:.1f} KB)")
        successful += 1
        
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        failed += 1

# ============================================
# SUMMARY
# ============================================

print(f"\n{'=' * 60}")
print(f"BATCH PROCESSING COMPLETE")
print(f"{'=' * 60}")
print(f"Successful: {successful}")
print(f"Failed:     {failed}")
print(f"Skipped:    {skipped}")
print(f"Total:      {len(BUFFER_DISTANCES)}")
print(f"\nOutput location: {EXCLUSIONS_DIR}")
print(f"{'=' * 60}")
