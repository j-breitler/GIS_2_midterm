"""
Simple slope calculator for SRTM DEM
Calculates slope from digital elevation model using basic Python
"""

import numpy as np
import rasterio
from pathlib import Path
import matplotlib.pyplot as plt

def calculate_slope_from_dem(dem_path, output_path=None):
    """
    Calculate slope from a Digital Elevation Model (DEM)

    Parameters:
    dem_path (str): Path to the DEM file (.tif)
    output_path (str, optional): Path to save slope raster. If None, saves in same directory
    """

    print(f"Opening DEM file: {dem_path}")

    # Open the DEM file
    with rasterio.open(dem_path) as dem:
        # Read the elevation data
        elevation = dem.read(1)  # Read the first band
        profile = dem.profile.copy()  # Get metadata

        print(f"DEM shape: {elevation.shape}")
        print(f"DEM CRS: {dem.crs}")
        print(f"DEM resolution: {dem.res}")

        # Get pixel size (resolution)
        pixel_size_x = abs(dem.res[0])  # Resolution in coordinate units
        pixel_size_y = abs(dem.res[1])

        # Check if coordinates are geographic (degrees) or projected (meters)
        if dem.crs.is_geographic:
            print("Warning: DEM is in geographic coordinates (degrees)")
            print("Pixel size in degrees:", pixel_size_x, "x", pixel_size_y)
            # For geographic coordinates, convert to approximate meters at equator
            # 1 degree ≈ 111,000 meters at equator
            pixel_size_x_meters = pixel_size_x * 111000
            pixel_size_y_meters = pixel_size_y * 111000
            print(".1f")
        else:
            pixel_size_x_meters = pixel_size_x
            pixel_size_y_meters = pixel_size_y
            print(".1f")

        # Calculate slope using simple finite differences
        print("Calculating slope...")

        # Calculate gradients in x and y directions (using meters)
        dz_dx = np.gradient(elevation, pixel_size_x_meters, axis=1)  # Change in elevation over x
        dz_dy = np.gradient(elevation, pixel_size_y_meters, axis=0)  # Change in elevation over y

        # Calculate slope in degrees
        # Slope = arctan(sqrt((dz/dx)^2 + (dz/dy)^2))
        slope_radians = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        slope_degrees = np.degrees(slope_radians)

        print("Slope calculation completed!")
        print(".2f")
        print(".2f")

        # Set output path
        if output_path is None:
            dem_path_obj = Path(dem_path)
            # Save slope raster to results/rasters folder
            results_rasters_dir = Path("data/results/rasters")
            results_rasters_dir.mkdir(parents=True, exist_ok=True)
            output_path = results_rasters_dir / f"{dem_path_obj.stem}_slope.tif"

        # Update profile for slope raster
        profile.update(dtype=rasterio.float32, count=1)

        # Save slope raster
        print(f"Saving slope raster to: {output_path}")
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(slope_degrees.astype(np.float32), 1)

        # Optional: Create a simple visualization
        print("\nCreating slope visualization...")
        plt.figure(figsize=(12, 8))
        plt.imshow(slope_degrees, cmap='terrain', vmin=0, vmax=50)
        plt.colorbar(label='Slope (degrees)')
        plt.title('Slope Map - Südoststeiermark')
        plt.axis('off')

        # Save visualization to results/figures folder
        results_figures_dir = Path("data/results/figures")
        results_figures_dir.mkdir(parents=True, exist_ok=True)
        viz_path = results_figures_dir / f"{output_path.stem}_visualization.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualization saved to: {viz_path}")
        return output_path, viz_path

def main():
    """Main function to run slope calculation"""

    # Path to the SRTM DEM file
    dem_file = "data/preprocessed/SRTM_DEM_30m_Suedoststeiermark_ERTS4326.tif"

    # Check if file exists
    if not Path(dem_file).exists():
        print(f"Error: DEM file not found at {dem_file}")
        print("Please check the file path and try again.")
        return

    try:
        # Calculate slope
        slope_file, viz_file = calculate_slope_from_dem(dem_file)

        print("\nSuccess! Slope calculated and saved.")
        print(f"Slope file: {slope_file}")
        print(f"Visualization: {viz_file}")

        # Optional: Show some basic statistics
        with rasterio.open(slope_file) as slope_raster:
            slope_data = slope_raster.read(1)
            print("\nSlope Statistics:")
            print(".2f")
            print(".2f")
            print(".2f")

    except Exception as e:
        print(f"Error during slope calculation: {e}")
        print("Please check your DEM file and try again.")

if __name__ == "__main__":
    main()