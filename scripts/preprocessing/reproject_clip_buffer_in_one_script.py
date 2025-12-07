"""
Preprocessing scripts for GIS-based PV potential assessment in Austria
"""

#Task
#Reproject shapefiles to UTM 33N
#Setup
import os
os.environ["SHAPE_RESTORE_SHX"] = "YES"  
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

#Reproject and clip DGM 30m

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from pathlib import Path

# Paths
DEM_RAW = Path("data/raw/DEM_30m_SO.tif")  
IN_DIR = Path("data/processed/reprojected_utm33n")
OUT_DIR = Path("data/processed/clipped_southeaststyria")

DISTRICT_SHP = IN_DIR / "southeaststyria.shp"
DEM_REPROJECTED = IN_DIR / "DEM_utm33n.tif"
DEM_CLIPPED = OUT_DIR / "DEM_SO.tif"

TARGET_CRS = "EPSG:32633"  # UTM 33N


def process_dgm():
    IN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Reproject raw DEM to UTM 33N ---
    print(f"Reprojecting DEM: {DEM_RAW}")
    with rasterio.open(DEM_RAW) as src:
        transform, width, height = calculate_default_transform(
            src.crs, TARGET_CRS, src.width, src.height, *src.bounds
        )

        meta = src.meta.copy()
        meta.update({
            "crs": TARGET_CRS,
            "transform": transform,
            "width": width,
            "height": height,
        })

        with rasterio.open(DEM_REPROJECTED, "w", **meta) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=TARGET_CRS,
                    resampling=Resampling.bilinear,
                )

    print(f"  → Saved reprojected DEM to {DEM_REPROJECTED}")

    # --- Step 2: Clip to district ---
    print(f"Loading district boundary: {DISTRICT_SHP}")
    district = gpd.read_file(DISTRICT_SHP)
    mask_geom = district.union_all()

    print("Clipping DEM to district...")
    with rasterio.open(DEM_REPROJECTED) as src:
        out_image, out_transform = mask(src, [mask_geom], crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        })

        with rasterio.open(DEM_CLIPPED, "w", **out_meta) as dst:
            dst.write(out_image)

    print(f"  → Saved clipped DEM to {DEM_CLIPPED}")


if __name__ == "__main__":
    process_dgm()

#Task:
#Create buffer zones around shapefiles

# Input directory: clipped shapes
CLIPPED_DIR = Path("data/processed/clipped_southeaststyria")

# Output directory
BUFFERED_DIR = Path("data/processed/buffered_southeaststyria")

# Buffer distances (meters)
BUFFER_DIST = {
    "Powerlines_southeaststyria": 120,
    "Streets_southeaststyria": 100,
    "Railway_southeaststyria": 100,
    "Airport_southeaststyria": 5000,
    "UrbanArea_southeaststyria": 500,
    "Industry_southeaststyria": 500,
    "WaterBodies_southeaststyria": 0,
    "Natura200_southeaststyria": 300,
    "Forest_southeaststyria": 0,
}


def buffer_all():
    BUFFERED_DIR.mkdir(parents=True, exist_ok=True)

    for shp_path in CLIPPED_DIR.glob("*.shp"):
        stem = shp_path.stem

        if stem not in BUFFER_DIST:
            print(f"Skipping (no buffer config): {shp_path.name}")
            continue

        buffer_dist = BUFFER_DIST[stem]
        print(f"\nProcessing: {shp_path.name} (buffer = {buffer_dist} m)")

        gdf = gpd.read_file(shp_path)

        # Apply buffer only if distance > 0, otherwise just copy geometry
        if buffer_dist > 0:
            gdf["geometry"] = gdf.geometry.buffer(buffer_dist)
        else:
            print("  Buffer distance is 0 m → geometry unchanged.")

        out_path = BUFFERED_DIR / f"{stem}_buf.shp"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        gdf.to_file(out_path, mode="w")
        print(f"  → Saved buffered layer to {out_path}")

if __name__ == "__main__":
    buffer_all()        
