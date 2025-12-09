"""
Visualization script for the research area boundary.
Creates a simple map showing the study area (Suedoststeiermark).
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
    RESEARCH_AREA_PLOT,    # Output: research area figure
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

# Create output directory if needed
RESULTS_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# LOAD RASTER DATA
# ============================================
print(f"Loading region mask from {REGION_MASK}...")
with rasterio.open(REGION_MASK) as src:
    data = src.read(1)
    transform = src.transform
    crs = src.crs
    height, width = data.shape

print(f"Raster dimensions: {width} x {height} pixels")

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

x_ticks, y_ticks = get_latlon_ticks(transform, crs, width, height)

# ============================================
# PLOTTING
# ============================================
print("Creating plot...")
fig, ax = plt.subplots(figsize=(10, 10))

im = ax.imshow(data, cmap='gray', alpha=0.7)

# Axis labels
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Axis ticks
ax.set_xticks(np.linspace(0, width-1, len(x_ticks)))
ax.set_xticklabels([f"{lon:.4f}" for lon in x_ticks], rotation=45)
ax.set_yticks(np.linspace(0, height-1, len(y_ticks)))
ax.set_yticklabels([f"{lat:.4f}" for lat in y_ticks])

# Grid
ax.grid(True, color='black', linestyle='--', alpha=0.3)

# Title
ax.set_title('Research Area Südoststeiermark', fontsize=16)

plt.tight_layout()

# ============================================
# SAVE AND SHOW PLOT
# ============================================
print(f"Saving plot to {RESEARCH_AREA_PLOT}...")
plt.savefig(RESEARCH_AREA_PLOT, dpi=300, bbox_inches='tight')
print("Plot saved successfully!")

plt.show()
