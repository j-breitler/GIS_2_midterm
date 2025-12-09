"""
Visualization script for eligible/suitable areas.
Creates a map showing areas suitable for PV installation (after all exclusions).
"""

import sys
from pathlib import Path

# ============================================
# SETUP: Add project root to Python path
# ============================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================
# IMPORTS FROM CONFIG
# ============================================
from config import (
    REGION_MASK,           # Input: region mask raster
    MASTER_SUITABILITY,    # Input: master suitability raster
    ELIGIBLE_AREAS_PLOT,   # Output: eligible areas figure
    RESULTS_FIGURES_DIR,   # Output directory for figures
)

# ============================================
# OTHER IMPORTS
# ============================================
import rasterio
from rasterio.transform import xy
import matplotlib.pyplot as plt
import numpy as np
import pyproj
from matplotlib.patches import Patch

# Create output directory if needed
RESULTS_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# LOAD RASTER DATA
# ============================================
print(f"Loading region mask from {REGION_MASK}...")
with rasterio.open(REGION_MASK) as src_mask:
    data_mask = src_mask.read(1)
    transform_mask = src_mask.transform
    crs_mask = src_mask.crs
    height_mask, width_mask = data_mask.shape

print(f"Loading master suitability from {MASTER_SUITABILITY}...")
with rasterio.open(MASTER_SUITABILITY) as src_suit:
    data_suit = src_suit.read(1)
    transform_suit = src_suit.transform
    crs_suit = src_suit.crs
    height_suit, width_suit = data_suit.shape

print(f"Region mask dimensions: {width_mask} x {height_mask} pixels")
print(f"Suitability dimensions: {width_suit} x {height_suit} pixels")

# ============================================
# AXIS CONVERSION TO LAT/LON
# ============================================
def get_latlon_ticks(transform, crs, width, height, num_ticks=5):
    """Generate tick values for x and y axes in Lat/Lon."""
    xs = np.linspace(0, width-1, num_ticks)
    ys = np.linspace(0, height-1, num_ticks)

    lon_ticks = []
    lat_ticks = []

    # Create transformer if CRS is not WGS84
    transformer = None
    if crs.to_string() != 'EPSG:4326':
        transformer = pyproj.Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)

    for x in xs:
        for y in ys:
            lon, lat = xy(transform, y, x)
            if transformer:
                lon, lat = transformer.transform(lon, lat)
            lon_ticks.append(lon)
            lat_ticks.append(lat)

    return np.unique(lon_ticks), np.unique(lat_ticks)

x_ticks_mask, y_ticks_mask = get_latlon_ticks(transform_mask, crs_mask, width_mask, height_mask, num_ticks=5)

# ============================================
# PLOTTING
# ============================================
print("Creating plot...")
fig, ax = plt.subplots(figsize=(10, 10))

# Master suitability plot (green for eligible areas)
suit_img = ax.imshow(data_suit == 1, cmap=None, alpha=0.7, vmin=0, vmax=1)
suit_img.set_cmap(plt.cm.get_cmap('Greens'))

# Region mask contour (black outline)
ax.contour(data_mask, levels=[0.5], colors='black', linewidths=1.5, alpha=0.7)

# Axis labels
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Axis ticks
ax.set_xticks(np.linspace(0, width_mask-1, len(x_ticks_mask)))
ax.set_xticklabels([f"{lon:.4f}" for lon in x_ticks_mask], rotation=45)
ax.set_yticks(np.linspace(0, height_mask-1, len(y_ticks_mask)))
ax.set_yticklabels([f"{lat:.4f}" for lat in y_ticks_mask])

# Grid
ax.grid(True, color='black', linestyle='--', alpha=0.3)

# Title
ax.set_title('Eligible Areas for Photovoltaics', fontsize=16)

# Legend
legend_handles = [
    Patch(facecolor='green', edgecolor='black', label='Eligible Area'),
    Patch(facecolor='none', edgecolor='black', linewidth=1.5, label='Region Mask')
]
ax.legend(handles=legend_handles, loc='upper right')

plt.tight_layout()

# ============================================
# SAVE AND SHOW PLOT
# ============================================
print(f"Saving plot to {ELIGIBLE_AREAS_PLOT}...")
plt.savefig(ELIGIBLE_AREAS_PLOT, dpi=300, bbox_inches='tight')
print("Plot saved successfully!")

plt.show()
