"""
Reproject and clip DEM to study area

This script:
1. Reprojects the raw DEM to the target CRS (UTM 33N)
2. Clips it to the study area boundary (Suedoststeiermark)
3. Saves only the final clipped result (no intermediate files)

Input:  Raw DEM (from config.DEM_RAW)
Output: Clipped DEM in target CRS (saved to preprocessed folder)
"""

import sys
from pathlib import Path

# ============================================
# SETUP: Add project root to Python path
# ============================================
# This allows us to import config.py from the project root
# Path(__file__) = this script's location
# .parent.parent.parent = go up 3 levels: preprocessing -> scripts -> project_root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================
# IMPORTS FROM CONFIG
# ============================================
# Now we can import paths and settings from our central config file
# Instead of hardcoding paths, we use the ones defined in config.py
from config import (
    DEM_RAW,               # Input: raw DEM file
    STUDY_AREA_SHAPEFILE,  # Clip boundary: study area shapefile
    PREPROCESSED_DIR,      # Output directory for processed files
    TARGET_CRS,            # Target coordinate system (EPSG:32633)
)

# ============================================
# OTHER IMPORTS
# ============================================
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from rasterio.io import MemoryFile

# ============================================
# OUTPUT PATH
# ============================================
# Final output: reprojected AND clipped to study area
DEM_CLIPPED = PREPROCESSED_DIR / "DEM_clipped.tif"


def process_dem():
    """
    Reproject and clip the DEM in one step.

    Steps:
    1. Read raw DEM
    2. Reproject to target CRS (in memory)
    3. Clip to study area (in memory)
    4. Save only the final clipped result

    This saves disk space by not storing intermediate reprojected files.
    """
    print("=" * 60)
    print("REPROJECT AND CLIP DEM")
    print("=" * 60)
    print(f"Input:      {DEM_RAW}")
    print(f"Output:     {DEM_CLIPPED}")
    print(f"Target CRS: {TARGET_CRS}")
    print()

    # Create output directory if it doesn't exist
    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Load and reproject study area boundary
    print("Loading study area boundary...")
    study_area = gpd.read_file(STUDY_AREA_SHAPEFILE)
    study_area_utm = study_area.to_crs(TARGET_CRS)
    clip_geometry = study_area_utm.union_all()
    print(f"  [OK] Study area loaded and reprojected to {TARGET_CRS}")

    # Open source DEM
    print("\nProcessing DEM...")
    with rasterio.open(DEM_RAW) as src:
        print(f"  Source CRS: {src.crs}")
        print(f"  Source size: {src.width} x {src.height} pixels")

        # Calculate transform for reprojection
        transform, width, height = calculate_default_transform(
            src.crs, TARGET_CRS, src.width, src.height, *src.bounds
        )

        # Prepare metadata for reprojected raster
        reproj_meta = src.meta.copy()
        reproj_meta.update({
            "crs": TARGET_CRS,
            "transform": transform,
            "width": width,
            "height": height,
        })

        # Use MemoryFile to reproject in memory (no disk write)
        print("  Reprojecting to UTM 33N (in memory)...")
        with MemoryFile() as memfile:
            # Write reprojected data to memory
            with memfile.open(**reproj_meta) as mem_dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(mem_dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=TARGET_CRS,
                        resampling=Resampling.bilinear,
                    )

            # Now clip the in-memory reprojected raster
            print("  Clipping to study area...")
            with memfile.open() as mem_src:
                # Clip raster to study area
                out_image, out_transform = mask(mem_src, [clip_geometry], crop=True)

                # Prepare metadata for final output
                out_meta = mem_src.meta.copy()
                out_meta.update({
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                })

                # Write final clipped raster to disk
                print("  Saving final result...")
                with rasterio.open(DEM_CLIPPED, "w", **out_meta) as dst:
                    dst.write(out_image)

    # Summary
    print(f"\n  [OK] Saved to {DEM_CLIPPED.name}")
    print(f"  Final size: {out_meta['width']} x {out_meta['height']} pixels")

    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Output location: {PREPROCESSED_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    process_dem()
