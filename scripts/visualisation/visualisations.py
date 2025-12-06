import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import os

#Load Data
shapefile_path = "data/processed/buffered_southeaststyria/Streets_southeaststyria_buf.shp"
gdf = gpd.read_file(shapefile_path)

#Directory for Results
output_dir = "data/Test_Resultate"
os.makedirs(output_dir, exist_ok=True)

#Plotting
fig, ax = plt.subplots(figsize=(10, 10))

# Reproject GeoDataFrame so it fits to plot (With Lat Lon Axes)
gdf_3857 = gdf.to_crs(epsg=3857)

# Plot vector data
gdf_3857.plot(ax=ax, color="blue", edgecolor="black", alpha=0.6)

# Add basemap (works only in Web Mercator)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

# Set axes limits to match data extent
xlim, ylim = gdf_3857.total_bounds[[0, 2]], gdf_3857.total_bounds[[1, 3]]
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# Convert Web Mercator coordinates to Lat/Lon for labeling
import numpy as np
import pyproj

# Transformer from EPSG:3857 -> EPSG:4326
transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

# Create tick positions and labels
xticks = np.linspace(xlim[0], xlim[1], num=5)
yticks = np.linspace(ylim[0], ylim[1], num=5)

xticklabels, yticklabels = [], []
for x in xticks:
    lon, _ = transformer.transform(x, ylim[0])
    xticklabels.append(f"{lon:.3f}")
for y in yticks:
    _, lat = transformer.transform(xlim[0], y)
    yticklabels.append(f"{lat:.3f}")

ax.set_xticks(xticks)
ax.set_yticks(yticks)
ax.set_xticklabels(xticklabels)
ax.set_yticklabels(yticklabels)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Test Visualisation of Street Shape")

#Save plot as .png
output_path = os.path.join(output_dir, "test_visualisation.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight", transparent=False)
plt.close(fig)

print(f"Plot saved at: {output_path}")
