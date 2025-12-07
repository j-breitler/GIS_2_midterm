import os
import rasterio

# Path for proj_data in Rasterio package
proj_data_path = os.path.join(os.path.dirname(rasterio.__file__), "proj_data")
os.environ['PROJ_LIB'] = proj_data_path

import matplotlib.pyplot as plt
from rasterio.transform import rowcol, xy
import numpy as np


#Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
tif_path = os.path.join(script_dir, "..", "..", "data", "preprocessed", "region_mask_100m.tif")
tif_path = os.path.normpath(tif_path)

#TIF
with rasterio.open(tif_path) as src:
    data = src.read(1)
    transform = src.transform
    crs = src.crs
    height, width = data.shape

#Axis change to Lat Lon
def get_latlon_ticks(src, num_ticks=5):
    """Erzeugt Tickwerte für x und y in Lat/Lon."""
    xs = np.linspace(0, width-1, num_ticks)
    ys = np.linspace(0, height-1, num_ticks)

    lon_ticks = []
    lat_ticks = []

    for x in xs:
        for y in ys:
            lon, lat = xy(transform, y, x) 
            if crs.to_string() != 'EPSG:4326':
                import pyproj
                transformer = pyproj.Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
                lon, lat = transformer.transform(lon, lat)
            lon_ticks.append(lon)
            lat_ticks.append(lat)

    return np.unique(lon_ticks), np.unique(lat_ticks)

x_ticks, y_ticks = get_latlon_ticks(src)

#Plotting 
fig, ax = plt.subplots(figsize=(10, 10))

im = ax.imshow(data, cmap='gray', alpha=0.7)

# Colorbar
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Axis-Ticks
ax.set_xticks(np.linspace(0, width-1, len(x_ticks)))
ax.set_xticklabels([f"{lon:.4f}" for lon in x_ticks], rotation=45)
ax.set_yticks(np.linspace(0, height-1, len(y_ticks)))
ax.set_yticklabels([f"{lat:.4f}" for lat in y_ticks])

# Raster
ax.grid(True, color='black', linestyle='--', alpha=0.3)

# Title
ax.set_title('Research Area Südoststeiermark', fontsize=16)

plt.tight_layout()

#save plot
output_dir = r"data/results/figures"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "research_area_plot.png")
plt.savefig(output_file, dpi=300, bbox_inches='tight')

#show plot
plt.show()

