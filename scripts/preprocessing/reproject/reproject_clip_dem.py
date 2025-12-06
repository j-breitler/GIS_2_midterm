#Reproject and clip DEM 30m

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from pathlib import Path

# Paths
DEM_RAW = Path("data/raw/DEM_30m_SO.tif")  # <-- your input DEM
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