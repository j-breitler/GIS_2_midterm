"""
Data acquisition and preprocessing script
Downloads and processes geospatial data for Austria PV potential assessment
"""

import requests
import os
from pathlib import Path

class DataDownloader:
    """Handles downloading and preprocessing of geospatial data"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def download_glo30_dem(self):
        """
        Download GLO-30 Digital Elevation Model from Copernicus
        This is a 30m resolution global DEM
        """
        print("Starting GLO-30 DEM download...")

        # GLO-30 download URL for Austria (example tile)
        # Note: You would need to find the specific tile URLs for Austria
        # This is a placeholder - in reality you'd need the actual Copernicus API or direct download links

        dem_url = "https://example.copernicus.eu/dem/glo30/austria_tile.tif"  # Placeholder URL
        output_file = self.raw_dir / "glo30_austria_dem.tif"

        try:
            print(f"Downloading from: {dem_url}")
            print(f"Saving to: {output_file}")

            # Download the file
            response = requests.get(dem_url)
            response.raise_for_status()  # Check if download was successful

            # Save the file
            with open(output_file, 'wb') as f:
                f.write(response.content)

            print(f"Successfully downloaded GLO-30 DEM to {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading GLO-30 DEM: {e}")
            print("Note: This is a placeholder. You need to find the actual Copernicus GLO-30 download URLs.")

        except Exception as e:
            print(f"Unexpected error: {e}")