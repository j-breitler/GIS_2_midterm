"""
Reproject and clip shapefiles to study area

This script:
1. Reprojects all constraint shapefiles to the target CRS (UTM 33N)
2. Clips them to the study area boundary (Suedoststeiermark)
3. Saves only the final clipped result (no intermediate files)

Input:  Raw shapefiles (from config.RAW_VECTORS)
Output: Clipped shapefiles in target CRS (saved to preprocessed folder)
"""

import sys
import os
from pathlib import Path

# Fix for missing .shx files (common with some shapefiles)
os.environ["SHAPE_RESTORE_SHX"] = "YES"

# ============================================
# SETUP: Add project root to Python path
# ============================================
# This allows us to import config.py from the project root
# .parent.parent.parent = go up 3 levels: preprocessing -> scripts -> project_root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================
# IMPORTS FROM CONFIG
# ============================================
from config import (
    RAW_VECTORS,           # Dictionary of constraint shapefiles
    STUDY_AREA_SHAPEFILE,  # Clip boundary: study area shapefile
    PREPROCESSED_DIR,      # Output directory for processed files
    TARGET_CRS,            # Target coordinate system (EPSG:32633)
)

# ============================================
# OTHER IMPORTS
# ============================================
import geopandas as gpd

# ============================================
# OUTPUT DIRECTORY
# ============================================
# Final output: reprojected AND clipped to study area
CLIPPED_DIR = PREPROCESSED_DIR / "clipped"


def reproject_and_clip_all():
    """
    Reproject and clip all constraint shapefiles in one step.

    For each shapefile:
    1. Load from raw data
    2. Reproject to target CRS (in memory)
    3. Clip to study area (in memory)
    4. Save only the final clipped result

    This saves disk space by not storing intermediate reprojected files.
    """
    print("=" * 60)
    print("REPROJECT AND CLIP SHAPEFILES")
    print("=" * 60)
    print(f"Input shapefiles: {len(RAW_VECTORS)}")
    print(f"Study area: {STUDY_AREA_SHAPEFILE.name}")
    print(f"Target CRS: {TARGET_CRS}")
    print(f"Output dir: {CLIPPED_DIR}")
    print()

    CLIPPED_DIR.mkdir(parents=True, exist_ok=True)

    # Load and reproject the study area boundary first
    print("Loading study area boundary...")
    study_area = gpd.read_file(STUDY_AREA_SHAPEFILE)
    study_area_utm = study_area.to_crs(TARGET_CRS)

    # Create single geometry for clipping (union of all features)
    clip_mask = study_area_utm.union_all()
    print(f"  [OK] Study area loaded and reprojected to {TARGET_CRS}")
    print()

    # Process each constraint shapefile
    for name, shp_path in RAW_VECTORS.items():
        print(f"Processing: {name}")

        # Check if file exists
        if not shp_path.exists():
            print(f"  [SKIP] File not found: {shp_path}")
            continue

        # Step 1: Load
        gdf = gpd.read_file(shp_path)
        print(f"  Source CRS: {gdf.crs}")
        print(f"  Features loaded: {len(gdf)}")

        # Step 2: Reproject (in memory)
        gdf_utm = gdf.to_crs(TARGET_CRS)

        # Store original geometry types (for filtering after clip)
        original_geom_types = set(gdf_utm.geometry.geom_type)

        # Step 3: Clip (in memory)
        clipped = gpd.clip(gdf_utm, clip_mask)

        if clipped.empty:
            print("  [SKIP] Result empty after clipping")
            continue

        # Keep only the original geometry types (avoid artifacts from clipping)
        if original_geom_types.issubset({"Polygon", "MultiPolygon"}):
            clipped = clipped[clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
        elif original_geom_types.issubset({"LineString", "MultiLineString"}):
            clipped = clipped[clipped.geometry.geom_type.isin(["LineString", "MultiLineString"])]
        elif original_geom_types.issubset({"Point", "MultiPoint"}):
            clipped = clipped[clipped.geometry.geom_type.isin(["Point", "MultiPoint"])]

        if clipped.empty:
            print("  [SKIP] Empty after geometry type filter")
            continue

        print(f"  Features after clip: {len(clipped)}")

        # Step 4: Save final result
        out_path = CLIPPED_DIR / f"{name}_clipped.shp"
        clipped.to_file(out_path, mode="w")
        print(f"  [OK] Saved to {out_path.name}")

    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Output location: {CLIPPED_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    reproject_and_clip_all()
