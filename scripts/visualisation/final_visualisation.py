import os
import rasterio
import matplotlib.pyplot as plt
from rasterio.transform import xy
import numpy as np
import pyproj
from matplotlib.patches import Patch

# PROJ_LIB
proj_data_path = os.path.join(os.path.dirname(rasterio.__file__), "proj_data")
os.environ['PROJ_LIB'] = proj_data_path

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))

# Region Mask
mask_path = os.path.join(script_dir, "..", "..", "data", "preprocessed", "region_mask_100m.tif")
mask_path = os.path.normpath(mask_path)

# Master Suitability (ICOE Aligned)
suit_path = os.path.join(script_dir, "..", "..", "data", "results", "rasters", "lcoe_aligned.tif")
suit_path = os.path.normpath(suit_path)

# TIFs einlesen
with rasterio.open(mask_path) as src_mask:
    data_mask = src_mask.read(1)
    transform_mask = src_mask.transform
    crs_mask = src_mask.crs
    height_mask, width_mask = data_mask.shape

with rasterio.open(suit_path) as src_suit:
    data_suit = src_suit.read(1)
    transform_suit = src_suit.transform
    crs_suit = src_suit.crs
    height_suit, width_suit = data_suit.shape

# Funktion für Lat/Lon-Ticks
def get_latlon_ticks(transform, crs, width, height, num_ticks=5):
    xs = np.linspace(0, width-1, num_ticks)
    ys = np.linspace(0, height-1, num_ticks)

    lon_ticks = []
    lat_ticks = []

    for x in xs:
        for y in ys:
            lon, lat = xy(transform, y, x)
            if crs.to_string() != 'EPSG:4326':
                transformer = pyproj.Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
                lon, lat = transformer.transform(lon, lat)
            lon_ticks.append(lon)
            lat_ticks.append(lat)

    return np.unique(lon_ticks), np.unique(lat_ticks)

x_ticks_mask, y_ticks_mask = get_latlon_ticks(transform_mask, crs_mask, width_mask, height_mask, num_ticks=5)

# Plot erstellen
fig, ax = plt.subplots(figsize=(10, 10))

# Master Suitability mit grüner Colormap plotten
suit_img = ax.imshow(data_suit, cmap='inferno', alpha=0.7)
cbar = fig.colorbar(suit_img, ax=ax, fraction=0.036, pad=0.04)
cbar.set_label('kWh/year', rotation=270, labelpad=15)

# Region Mask Kontur schwarz
ax.contour(data_mask, levels=[0.5], colors='black', linewidths=1.5, alpha=0.7)

# Achsen
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_xticks(np.linspace(0, width_mask-1, len(x_ticks_mask)))
ax.set_xticklabels([f"{lon:.4f}" for lon in x_ticks_mask], rotation=45)
ax.set_yticks(np.linspace(0, height_mask-1, len(y_ticks_mask)))
ax.set_yticklabels([f"{lat:.4f}" for lat in y_ticks_mask])

# Raster
ax.grid(True, color='black', linestyle='--', alpha=0.3)

# Titel
ax.set_title('Photovoltaic Potential in Südoststeiermark', fontsize=16)

# Legende für Region Mask
legend_handles = [
    Patch(facecolor='none', edgecolor='black', linewidth=1.5, label='Südoststeiermark')
]
ax.legend(handles=legend_handles, loc='upper right')

plt.tight_layout()

#save plot
output_dir = r"data/results/figures"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "FINAL_VISUALISATION.png")
plt.savefig(output_file, dpi=300, bbox_inches='tight')

#show plot
plt.show()
