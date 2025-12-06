"""
Project Configuration
Defines all paths and settings for the GIS analysis project
Solar PV Suitability Analysis - Suedoststeiermark, Austria

HOW TO USE THIS FILE:
---------------------
1. Import what you need in your scripts:

   from config import STUDY_AREA_SHAPEFILE, TARGET_CRS, RESOLUTION

2. Or import everything:

   import config
   # Then use: config.STUDY_AREA_SHAPEFILE

3. Run this file directly to check your setup:

   python config.py
"""

import os
from pathlib import Path

# ============================================
# FIX FOR PROJ LIBRARY CONFLICT
# ============================================
# This fixes a common issue on Windows when you have PostGIS, QGIS, or other
# GIS software installed. These programs install their own PROJ library which
# can conflict with Python's pyproj/rasterio.
#
# This code finds the correct PROJ data directory from pyproj and sets it
# as an environment variable BEFORE any GIS libraries are imported.
#
# If you don't have this conflict, this code does nothing harmful - it just
# explicitly tells Python where to find PROJ data.

def _setup_proj_lib():
    """
    Set PROJ_LIB environment variable to avoid conflicts with other GIS software.
    This runs automatically when config is imported.
    """
    try:
        import pyproj
        # Get the PROJ data directory from pyproj
        proj_dir = pyproj.datadir.get_data_dir()
        if proj_dir and Path(proj_dir).exists():
            os.environ['PROJ_LIB'] = proj_dir
    except ImportError:
        # pyproj not installed yet - that's fine, skip this
        pass
    except Exception:
        # Any other error - don't crash, just skip
        pass

# Run the fix immediately when config is imported
_setup_proj_lib()

# ============================================
# PROJECT ROOT DIRECTORY
# ============================================
# Path(__file__) = the path to THIS config.py file
# .parent = the folder containing this file (project root)
# .resolve() = converts to absolute path (no relative "../" parts)
# This way, paths work no matter where you run your scripts from
PROJECT_ROOT = Path(__file__).parent.resolve()

# ============================================
# DATA DIRECTORIES
# ============================================
# Using "/" with Path objects joins paths (works on Windows too!)
# Example: PROJECT_ROOT / "data" creates "C:/...project.../data"

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"              # Original, unmodified input data
PREPROCESSED_DIR = DATA_DIR / "preprocessed"  # Intermediate processing outputs
PROCESSED_DIR = DATA_DIR / "processed"        # Fully processed data
RESULTS_DIR = DATA_DIR / "results"            # Final outputs (maps, reports)

# Results subdirectories - keeps outputs organized by type
RESULTS_FIGURES_DIR = RESULTS_DIR / "figures"   # PNG, JPG maps and charts
RESULTS_RASTERS_DIR = RESULTS_DIR / "rasters"   # Output GeoTIFFs
RESULTS_VECTORS_DIR = RESULTS_DIR / "vectors"   # Output shapefiles
RESULTS_REPORTS_DIR = RESULTS_DIR / "reports"   # Text reports, CSVs
RESULTS_TEMP_DIR = RESULTS_DIR / "temp"         # Temporary files (can be deleted)

# ============================================
# SCRIPT DIRECTORIES
# ============================================
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
PREPROCESSING_DIR = SCRIPTS_DIR / "preprocessing"  # Data preparation scripts
ANALYSIS_DIR = SCRIPTS_DIR / "analysis"            # Analysis/calculation scripts
VISUALISATION_DIR = SCRIPTS_DIR / "visualisation"  # Plotting/mapping scripts

# ============================================
# OTHER DIRECTORIES
# ============================================
DOCS_DIR = PROJECT_ROOT / "docs"           # Documentation and methodology
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"  # Jupyter notebooks

# ============================================
# RAW INPUT DATA - RASTERS
# ============================================
# Raster = grid of pixels with values (like an image with data)

# Digital Elevation Model - height above sea level for each pixel
# Used to calculate slope (steep areas are unsuitable for PV)
DEM_RAW = RAW_DATA_DIR / "Raster" / "DEM" / "SRTM_DEM_30m_SO.tif"

# Solar PV Output potential - expected electricity generation
# Values represent kWh/kWp/year (kilowatt-hours per kilowatt-peak per year)
PVOUT_RAW = RAW_DATA_DIR / "Raster" / "PVOUT.tif"

# ============================================
# RAW INPUT DATA - STUDY AREA BOUNDARY
# ============================================
# This shapefile defines the boundary of Suedoststeiermark district
# All analysis is clipped to this area
STUDY_AREA_SHAPEFILE = RAW_DATA_DIR / "Study_Area_Vector" / "Suedoststeiermark_Shapefile.shp"

# ============================================
# RAW INPUT DATA - CONSTRAINT VECTORS
# ============================================
# These shapefiles represent areas where PV installation is restricted
# Dictionary format: {"short_name": path_to_file}
# Short names match the keys in BUFFER_DISTANCES below

RAW_VECTORS = {
    "airport": RAW_DATA_DIR / "Vector" / "Airport_Styria.shp",
    "forest": RAW_DATA_DIR / "Vector" / "Forest_Styria.shp",
    "industry": RAW_DATA_DIR / "Vector" / "Industry_Styria.shp",
    "natura2000": RAW_DATA_DIR / "Vector" / "Natura200_Styria.shp",  # Protected nature areas
    "powerlines": RAW_DATA_DIR / "Vector" / "Powerlines_Styria.shp",
    "railway": RAW_DATA_DIR / "Vector" / "Railway_Styria.shp",
    "streets": RAW_DATA_DIR / "Vector" / "Streets_Styria.shp",
    "urban_area": RAW_DATA_DIR / "Vector" / "UrbanArea_Styria.shp",
    "water_bodies": RAW_DATA_DIR / "Vector" / "WaterBodies_Styria.shp",
}

# ============================================
# PREPROCESSED OUTPUTS
# ============================================
# Region mask = raster covering study area where:
#   1 = inside study area (potentially suitable)
#   0 = outside study area
# This serves as the "canvas" for exclusion analysis
REGION_MASK = PREPROCESSED_DIR / "region_mask_100m.tif"

# ============================================
# ANALYSIS SETTINGS
# ============================================
# CRS = Coordinate Reference System
# EPSG:32633 = UTM Zone 33N - a projected CRS suitable for Austria
# Projected CRS uses meters (good for distance/area calculations)
# WGS84 (EPSG:4326) uses degrees (not suitable for measurements)
TARGET_CRS = "EPSG:32633"

# Raster resolution in meters
# 100m = each pixel represents a 100m x 100m area (1 hectare)
# Smaller = more detail but larger files and slower processing
RESOLUTION = 100

# ============================================
# BUFFER DISTANCES (meters)
# ============================================
# Buffer = area around a feature that is also excluded
# Example: 120m buffer around powerlines means 120m on each side is excluded
# 0 = no buffer, only the feature itself is excluded

BUFFER_DISTANCES = {
    "powerlines": 120,    # Safety distance from power lines
    "streets": 100,       # Setback from roads
    "railway": 100,       # Setback from railways
    "airport": 5000,      # Large buffer for airports (flight paths, noise)
    "urban_area": 500,    # Distance from urban/residential areas
    "industry": 500,      # Distance from industrial zones
    "water_bodies": 0,    # Water bodies excluded, no additional buffer
    "natura2000": 300,    # Buffer around protected natural areas
    "forest": 0,          # Forests excluded, no additional buffer
}

# ============================================
# SLOPE CONSTRAINT
# ============================================
# Maximum slope angle in degrees for PV installation
# Steeper slopes are harder/more expensive to build on
# Typical thresholds: 10-20 degrees depending on technology
MAX_SLOPE_DEGREES = 15

# ============================================
# HELPER FUNCTIONS
# ============================================

def setup_directories():
    """
    Create all project directories if they don't exist.

    Call this at the start of your project or when setting up
    on a new computer. It won't overwrite existing folders.

    Usage:
        from config import setup_directories
        setup_directories()
    """
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PREPROCESSED_DIR,
        PROCESSED_DIR,
        RESULTS_DIR,
        RESULTS_FIGURES_DIR,
        RESULTS_RASTERS_DIR,
        RESULTS_VECTORS_DIR,
        RESULTS_REPORTS_DIR,
        RESULTS_TEMP_DIR,
        SCRIPTS_DIR,
        PREPROCESSING_DIR,
        ANALYSIS_DIR,
        VISUALISATION_DIR,
        DOCS_DIR,
        NOTEBOOKS_DIR,
    ]

    for directory in directories:
        # mkdir = make directory
        # parents=True = create parent folders if needed
        # exist_ok=True = don't error if folder already exists
        directory.mkdir(parents=True, exist_ok=True)

    print("All directories created/verified")


def check_raw_data():
    """
    Check if all required input files exist.

    Run this to verify your data is in the right place before
    starting analysis. Returns True if all files found.

    Usage:
        from config import check_raw_data
        check_raw_data()
    """
    print("\n" + "=" * 60)
    print("RAW DATA CHECK")
    print("=" * 60)

    all_found = True

    # Check rasters
    print("\nRasters:")
    for name, path in [("DEM", DEM_RAW), ("PVOUT", PVOUT_RAW)]:
        if path.exists():  # .exists() returns True if file is there
            print(f"  [OK] {name}: {path.name}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_found = False

    # Check study area
    print("\nStudy Area:")
    if STUDY_AREA_SHAPEFILE.exists():
        print(f"  [OK] {STUDY_AREA_SHAPEFILE.name}")
    else:
        print(f"  [MISSING] {STUDY_AREA_SHAPEFILE}")
        all_found = False

    # Check constraint vectors
    print("\nConstraint Vectors:")
    for name, path in RAW_VECTORS.items():
        if path.exists():
            print(f"  [OK] {name}: {path.name}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_found = False

    print("\n" + "=" * 60)
    if all_found:
        print("All raw data files found!")
    else:
        print("WARNING: Some files are missing!")
    print("=" * 60)

    return all_found


def print_config():
    """
    Print a summary of current configuration.

    Useful for debugging or documenting your analysis setup.

    Usage:
        from config import print_config
        print_config()
    """
    print("\n" + "=" * 60)
    print("PROJECT CONFIGURATION")
    print("=" * 60)
    print(f"Project Root:     {PROJECT_ROOT}")
    print(f"Raw Data Dir:     {RAW_DATA_DIR}")
    print(f"Preprocessed Dir: {PREPROCESSED_DIR}")
    print(f"Results Dir:      {RESULTS_DIR}")
    print(f"\nTarget CRS:       {TARGET_CRS}")
    print(f"Resolution:       {RESOLUTION}m")
    print(f"Max Slope:        {MAX_SLOPE_DEGREES} degrees")
    print(f"\nStudy Area:       {STUDY_AREA_SHAPEFILE.name}")
    print(f"Region Mask:      {REGION_MASK.name}")
    print("=" * 60 + "\n")


# ============================================
# RUN WHEN EXECUTED DIRECTLY
# ============================================
# This block only runs when you execute: python config.py
# It does NOT run when you import config in another script

if __name__ == "__main__":
    print_config()
    setup_directories()
    check_raw_data()
