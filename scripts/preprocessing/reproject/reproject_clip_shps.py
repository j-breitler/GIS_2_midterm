#Task
#Reproject shapefiles to UTM 33N
#Setup
import os
os.environ["SHAPE_RESTORE_SHX"] = "YES"   # <-- FIX for missing .shx files
from pathlib import Path
import geopandas as gpd

#Configuration
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed/reprojected_utm33n")
TARGET_CRS = "EPSG:32633"   # UTM 33N

# Reproject all shapefiles in RAW_DIR to TARGET_CRS and save to OUT_DIR
def reproject_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for shp_path in RAW_DIR.rglob("*.shp"):
        print(f"Reprojecting: {shp_path}")

        gdf = gpd.read_file(shp_path)

        # Force reproject regardless of current CRS
        gdf_utm = gdf.to_crs(TARGET_CRS)

        # Preserve folder structure inside processed folder
        rel = shp_path.relative_to(RAW_DIR)
        out_path = OUT_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        gdf_utm.to_file(out_path)
        print(f"  → Saved to {out_path}")

if __name__ == "__main__":
    reproject_all()


# Task:
# Clip all shapefiles to Südoststeiermark shapefile

# Setup

IN_DIR = Path("data/processed/reprojected_utm33n")
OUT_DIR = Path("data/processed/clipped_southeaststyria")
DISTRICT_SHP = Path("data/processed/reprojected_utm33n/southeaststyria.shp")


def clip_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading district shapefile: {DISTRICT_SHP}")
    district = gpd.read_file(DISTRICT_SHP)

    # Use union_all() to merge district geometries into one mask
    mask = district.union_all()

    for shp_path in IN_DIR.rglob("*.shp"):
        print(f"\nProcessing: {shp_path.name}")
        gdf = gpd.read_file(shp_path)

        geom_types = set(gdf.geometry.geom_type)

        # Clip the layer to the district boundary
        clipped = gpd.clip(gdf, mask)

        if clipped.empty:
            print("  → Result empty, skipped.")
            continue

        # Keep only the original geometry type to avoid artifacts
        if geom_types.issubset({"Polygon", "MultiPolygon"}):
            clipped = clipped[clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
        elif geom_types.issubset({"LineString", "MultiLineString"}):
            clipped = clipped[clipped.geometry.geom_type.isin(["LineString", "MultiLineString"])]
        else:
            # Unexpected geometry types → skip layer for safety
            print(f" Unexpected geometry types {geom_types}, skipped.")
            continue

        if clipped.empty:
            print("  → Empty after geometry filter, skipped.")
            continue

        # Rename layer: replace 'Styria' with 'SO'
        clean_stem = shp_path.stem.replace("_Styria", "_southeaststyria").replace("Styria", "_southeaststyria")

        out_path = OUT_DIR / f"{clean_stem}.shp"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        clipped.to_file(out_path, mode="w")
        print(f"  → Saved {out_path}")


if __name__ == "__main__":
    clip_all()
    