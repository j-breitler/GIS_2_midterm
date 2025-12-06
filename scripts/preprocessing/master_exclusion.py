"""
Create master exclusion / final suitability raster

This script:
1. Loads the region mask as baseline (1 = study area, 0 = outside)
2. Loops through all exclusion rasters in the exclusions folder
3. Combines them: any pixel excluded by ANY layer becomes 0
4. Outputs final suitability raster

Logic:
- Start with region_mask (1 = potentially suitable, 0 = outside)
- For each exclusion raster: where exclusion = 1, set suitability = 0
- Final result: 1 = suitable land, 0 = excluded or outside study area

Input:  region_mask_100m.tif + all *_exclusion.tif files
Output: master_suitability.tif (1 = suitable, 0 = not suitable)
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
    REGION_MASK,           # Baseline raster (study area)
    RESOLUTION,            # For area calculations
)

# ============================================
# OTHER IMPORTS
# ============================================
import rasterio
import numpy as np

# ============================================
# INPUT/OUTPUT PATHS
# ============================================
# Input: exclusion rasters
EXCLUSIONS_DIR = PREPROCESSED_DIR / "exclusions"

# Output: final suitability raster
MASTER_SUITABILITY_OUTPUT = PREPROCESSED_DIR / "master_suitability.tif"

print("=" * 60)
print("MASTER EXCLUSION / SUITABILITY ANALYSIS")
print("=" * 60)
print(f"Baseline:      {REGION_MASK}")
print(f"Exclusions:    {EXCLUSIONS_DIR}")
print(f"Output:        {MASTER_SUITABILITY_OUTPUT}")
print()

# ============================================
# STEP 1: LOAD REGION MASK AS BASELINE
# ============================================
print("[1/3] Loading region mask as baseline...")

with rasterio.open(REGION_MASK) as src:
    # Start with region mask: 1 = study area, 0 = outside
    suitability = src.read(1).astype(np.uint8)
    meta = src.meta.copy()
    transform = src.transform

# Calculate initial study area
pixel_area_km2 = (RESOLUTION * RESOLUTION) / 1e6  # Convert m² to km²
initial_pixels = np.sum(suitability == 1)
initial_area_km2 = initial_pixels * pixel_area_km2

print(f"  Study area pixels: {initial_pixels:,}")
print(f"  Study area: {initial_area_km2:.2f} km2")
print()

# ============================================
# STEP 2: APPLY EACH EXCLUSION
# ============================================
print("[2/3] Applying exclusions...")
print()

# Find all exclusion rasters (files ending with _exclusion.tif)
exclusion_files = sorted(EXCLUSIONS_DIR.glob("*_exclusion.tif"))

if not exclusion_files:
    print("  [WARNING] No exclusion files found!")
else:
    print(f"  Found {len(exclusion_files)} exclusion rasters:")
    print()

# Track statistics for each exclusion
exclusion_stats = []

for exclusion_path in exclusion_files:
    name = exclusion_path.stem.replace("_exclusion", "")
    
    # Load exclusion raster
    with rasterio.open(exclusion_path) as src:
        exclusion = src.read(1)
    
    # Count pixels BEFORE applying this exclusion
    suitable_before = np.sum(suitability == 1)
    
    # Apply exclusion: where exclusion = 1, set suitability = 0
    # Using bitwise AND with inverted exclusion: suitability AND (NOT exclusion)
    suitability = suitability & (~exclusion.astype(np.uint8))
    
    # Ensure values stay 0 or 1
    suitability = (suitability > 0).astype(np.uint8)
    
    # Count pixels AFTER applying this exclusion
    suitable_after = np.sum(suitability == 1)
    
    # Calculate how many pixels this exclusion removed
    pixels_removed = suitable_before - suitable_after
    area_removed_km2 = pixels_removed * pixel_area_km2
    
    # Store stats
    exclusion_stats.append({
        'name': name,
        'pixels_removed': pixels_removed,
        'area_removed_km2': area_removed_km2,
    })
    
    print(f"  {name:20s} removed {pixels_removed:>6,} pixels ({area_removed_km2:>6.2f} km2)")

print()

# ============================================
# STEP 3: SAVE FINAL SUITABILITY RASTER
# ============================================
print("[3/3] Saving final suitability raster...")

# Calculate final statistics
final_pixels = np.sum(suitability == 1)
final_area_km2 = final_pixels * pixel_area_km2
total_excluded_pixels = initial_pixels - final_pixels
total_excluded_area_km2 = total_excluded_pixels * pixel_area_km2
suitable_percent = (final_pixels / initial_pixels) * 100 if initial_pixels > 0 else 0

# Update metadata and save
output_meta = meta.copy()
output_meta.update({
    'dtype': 'uint8',
    'nodata': None,
    'compress': 'lzw'
})

with rasterio.open(MASTER_SUITABILITY_OUTPUT, 'w', **output_meta) as dst:
    dst.write(suitability, 1)

file_size_kb = os.path.getsize(MASTER_SUITABILITY_OUTPUT) / 1024
print(f"  [OK] Saved to {MASTER_SUITABILITY_OUTPUT.name} ({file_size_kb:.1f} KB)")

# ============================================
# SUMMARY
# ============================================
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Initial study area:     {initial_area_km2:>10.2f} km2 ({initial_pixels:,} pixels)")
print(f"Total excluded:         {total_excluded_area_km2:>10.2f} km2 ({total_excluded_pixels:,} pixels)")
print(f"Final suitable area:    {final_area_km2:>10.2f} km2 ({final_pixels:,} pixels)")
print(f"Suitable percentage:    {suitable_percent:>10.2f} %")
print()
print("Exclusion breakdown:")
print("-" * 60)
for stat in sorted(exclusion_stats, key=lambda x: x['area_removed_km2'], reverse=True):
    pct = (stat['pixels_removed'] / initial_pixels) * 100 if initial_pixels > 0 else 0
    print(f"  {stat['name']:20s} {stat['area_removed_km2']:>8.2f} km2  ({pct:>5.2f}%)")
print("-" * 60)
print()
print("Output interpretation:")
print("  1 = Suitable land (passed all exclusion criteria)")
print("  0 = Not suitable (excluded or outside study area)")
print("=" * 60)
