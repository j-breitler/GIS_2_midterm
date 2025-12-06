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
