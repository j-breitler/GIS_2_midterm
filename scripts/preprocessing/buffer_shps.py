"""
Create buffer zones around constraint shapefiles

This script:
1. Reads the clipped shapefiles (output from reproject_clip_shps.py)
2. Applies buffer distances from config.BUFFER_DISTANCES
3. Saves buffered shapefiles to preprocessed folder

Input:  Clipped shapefiles from PREPROCESSED_DIR/clipped/
Output: Buffered shapefiles in PREPROCESSED_DIR/buffered/
"""

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
    PREPROCESSED_DIR,      # Base directory for processed files
    BUFFER_DISTANCES,      # Dictionary of buffer distances per constraint
)

# ============================================
# OTHER IMPORTS
# ============================================
import geopandas as gpd

# ============================================
# INPUT/OUTPUT DIRECTORIES
# ============================================
# Input: clipped shapefiles from reproject_clip_shps.py
CLIPPED_DIR = PREPROCESSED_DIR / "clipped"

# Output: buffered shapefiles
BUFFERED_DIR = PREPROCESSED_DIR / "buffered"


def buffer_all():
    """
    Apply buffer zones to all clipped constraint shapefiles.
    
    Buffer distances are defined in config.BUFFER_DISTANCES.
    If buffer distance is 0, the geometry is copied unchanged.
    """
    print("=" * 60)
    print("BUFFER CONSTRAINT SHAPEFILES")
    print("=" * 60)
    print(f"Input dir:  {CLIPPED_DIR}")
    print(f"Output dir: {BUFFERED_DIR}")
    print()

    BUFFERED_DIR.mkdir(parents=True, exist_ok=True)

    # Process each constraint type defined in config
    for name, buffer_dist in BUFFER_DISTANCES.items():
        # Input file from clipped directory
        shp_path = CLIPPED_DIR / f"{name}_clipped.shp"

        if not shp_path.exists():
            print(f"[SKIP] {name}: clipped file not found")
            continue

        print(f"Processing: {name} (buffer = {buffer_dist} m)")

        # Load shapefile
        gdf = gpd.read_file(shp_path)
        print(f"  Features loaded: {len(gdf)}")

        # Apply buffer only if distance > 0
        if buffer_dist > 0:
            gdf["geometry"] = gdf.geometry.buffer(buffer_dist)
            print(f"  Buffer applied: {buffer_dist} m")
        else:
            print(f"  Buffer distance is 0 m - geometry unchanged")

        # Save buffered shapefile
        out_path = BUFFERED_DIR / f"{name}_buffered.shp"
        gdf.to_file(out_path, mode="w")
        print(f"  [OK] Saved to {out_path.name}")

    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Output location: {BUFFERED_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    buffer_all()
