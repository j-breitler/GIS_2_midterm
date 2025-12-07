import os
import rasterio
import matplotlib.pyplot as plt
from rasterio.transform import xy
import numpy as np
import pyproj
from matplotlib.patches import Patch

#PROJ_LIB
proj_data_path = os.path.join(os.path.dirname(rasterio.__file__), "proj_data")
os.environ['PROJ_LIB'] = proj_data_path

#Paths
script_dir = os.path.dirname(os.path.abspath(__file__))

# Region Mask
mask_path = os.path.join(script_dir, "..", "..", "data", "preprocessed", "region_mask_100m.tif")
mask_path = os.path.normpath(mask_path)

# Master Suitability
suit_path = os.path.join(script_dir, "..", "..", "data", "preprocessed", "master_suitability.tif")
suit_path = os.path.normpath(suit_path)

#TIFS
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

#Axis Change to Lat Lon
def get_latlon_ticks(transform, crs, width, height, num_ticks=5):
    """Erzeugt Tickwerte für x und y in Lat/Lon."""
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

#Plotting
fig, ax = plt.subplots(figsize=(10, 10))

# Master Suitability plot
suit_color = 'green'
suit_img = ax.imshow(data_suit == 1, cmap=None, alpha=0.7, vmin=0, vmax=1)
suit_img.set_cmap(plt.cm.get_cmap('Greens'))  


# Region Mask Contur
mask_contour = ax.contour(data_mask, levels=[0.5], colors='black', linewidths=1.5, alpha=0.7)

# Axis in Lat Lon
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Axis-Ticks
ax.set_xticks(np.linspace(0, width_mask-1, len(x_ticks_mask)))
ax.set_xticklabels([f"{lon:.4f}" for lon in x_ticks_mask], rotation=45)
ax.set_yticks(np.linspace(0, height_mask-1, len(y_ticks_mask)))
ax.set_yticklabels([f"{lat:.4f}" for lat in y_ticks_mask])

# Raster
ax.grid(True, color='black', linestyle='--', alpha=0.3)

# Title
ax.set_title('Eligible Areas for Photovoltaics', fontsize=16)

#Legend
legend_handles = [
    Patch(facecolor='green', edgecolor='black', label='Eligible Area'),
    Patch(facecolor='none', edgecolor='black', linewidth=1.5, label='Region Mask')
]

ax.legend(handles=legend_handles, loc='upper right')

plt.tight_layout()

#save plot
output_dir = r"data/results/figures"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "eligible_areas_plot.png")
plt.savefig(output_file, dpi=300, bbox_inches='tight')

#show plot
plt.show()

