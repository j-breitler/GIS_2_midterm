import pathlib
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

# --------------------------------------------------
# Base paths (only THIS block must be adapted locally)
# --------------------------------------------------
BASE = pathlib.Path(
    r"C:\1_Daten\01_UniGraz\2025 WiSe\VU GIS Analysis Techniques 2\midterm_project"
)
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"

# Input paths
pvout_raw   = RAW  / "PVOUT.tif"              # daily PV yield (kWh/kWp/day)
region_mask = PROC / "DATEINAME DER EIGNUNGSMASKE EINTRAGEN.tif"   # 0/1 mask of the study area (100 m)

# Output paths
pvout_utm     = PROC / "pvout_32633_100m.tif"        # PVOUT reprojected to UTM 33N
pvout_aligned = PROC / "pvout_aligned_to_mask.tif"   # PVOUT aligned to region mask
E_year_raster = PROC / "pvout_Eyear_aligned.tif"     # yearly PV yield
lcoe_raster   = PROC / "lcoe_aligned.tif"            # LCOE raster

SRC_CRS = "EPSG:4326"   # original PVOUT CRS (lat/lon)
DST_CRS = "EPSG:32633"  # target CRS (UTM 33N)
DST_RES = 100           # target resolution in metres


# --------------------------------------------------
# 1) Inspect original PVOUT raster
#    (CRS, geotransform, size, basic sanity check)
# --------------------------------------------------
with rasterio.open(pvout_raw) as src:
    print(src.crs)
    print(src.transform)
    print(src.width, src.height)
    pvout = src.read(1)


# --------------------------------------------------
# 2) Reproject PVOUT to UTM 33N with 100 m resolution
#    → creates a consistent metric grid for later analysis
# --------------------------------------------------
with rasterio.open(pvout_raw) as src:
    transform, width, height = calculate_default_transform(
        src.crs, DST_CRS, src.width, src.height, *src.bounds, resolution=DST_RES
    )
    kwargs = src.meta.copy()
    kwargs.update({
        "crs": DST_CRS,
        "transform": transform,
        "width": width,
        "height": height
    })

    with rasterio.open(pvout_utm, "w", **kwargs) as dst:
        reproject(
            source=rasterio.band(src, 1),
            destination=rasterio.band(dst, 1),
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=DST_CRS,
            resampling=Resampling.bilinear,
        )


# --------------------------------------------------
# 3) Align PVOUT raster to the region mask grid
#    (same extent, resolution, and transform as region_mask)
# --------------------------------------------------
with rasterio.open(region_mask) as mask, rasterio.open(pvout_utm) as src:
    dst_meta = mask.meta.copy()
    # use the mask's shape as template; data will be overwritten by reproject()
    dst_data = mask.read(1).astype("float32")

    reproject(
        source=rasterio.band(src, 1),
        destination=dst_data,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=mask.transform,
        dst_crs=mask.crs,
        resampling=Resampling.bilinear,
    )

    dst_meta.update(dtype="float32", nodata=None)

    with rasterio.open(pvout_aligned, "w", **dst_meta) as dst:
        dst.write(dst_data, 1)

# quick check of the aligned PVOUT raster
with rasterio.open(pvout_aligned) as src:
    print(src.crs)
    print(src.transform)
    band = src.read(1)
    print("Min/Max PVOUT aligned:", band.min(), band.max())


# --------------------------------------------------
# 4) Convert daily PV yield to yearly yield E_year
#    PVOUT is in kWh/kWp/day → multiply by 365
# --------------------------------------------------
with rasterio.open(pvout_aligned) as src:
    pv_daily = src.read(1).astype("float32")   # kWh/kWp per day
    meta = src.meta.copy()

E_year = pv_daily * 365.0                      # kWh/kWp per year
meta.update(dtype="float32", nodata=None)

with rasterio.open(E_year_raster, "w", **meta) as dst:
    dst.write(E_year, 1)


# --------------------------------------------------
# 5) Compute mean specific yearly yield over the study area
#    (only where region_mask == 1)
# --------------------------------------------------
with rasterio.open(region_mask) as msrc, rasterio.open(E_year_raster) as esrc:
    mask   = msrc.read(1)          # 0/1
    E_year = esrc.read(1)          # kWh/kWp/year

eligible = mask == 1
E_year_mean = E_year[eligible].mean()

print("Mean specific yearly yield:", E_year_mean, "kWh/kWp/a")
print("Unique mask values:", np.unique(mask))
print("Unique E_year (rounded, eligible):", np.unique(E_year[eligible].round(2))[:20])


# --------------------------------------------------
# 6) Compute LCOE raster using the paper's formula
#    LCOE = [ (H + 0.5*H)*CRF + I0*theta ] / E_year
#    with CRF = i(1+i)^N / ((1+i)^N - 1)
# --------------------------------------------------
def crf(i, N):
    """Capital Recovery Factor (CRF) for discount rate i and lifetime N."""
    return i * (1 + i) ** N / ((1 + i) ** N - 1)

# techno-economic parameters from Benalcázar et al. (2024)
H     = 545.6    # €/kW (CAPEX)
i     = 0.0592   # 5.92 % discount rate
N     = 25       # lifetime in years
theta = 0.01     # 1 % of I0 per year for O&M
I0    = H        # initial investment per kW

CRF = crf(i, N)
# numerator of the LCOE equation (annualised cost per kW)
num_cost = (H + 0.5 * H) * CRF + I0 * theta

with rasterio.open(E_year_raster) as esrc, rasterio.open(region_mask) as msrc:
    E_year = esrc.read(1).astype("float32")   # kWh/kWp/year
    mask   = msrc.read(1)

eligible = mask == 1

# initialise LCOE raster with NaN outside eligible area
lcoe = np.full(E_year.shape, np.nan, dtype="float32")
lcoe[eligible] = num_cost / E_year[eligible]   # €/kWh

meta = esrc.meta.copy()
meta.update(dtype="float32", nodata=np.nan)

with rasterio.open(lcoe_raster, "w", **meta) as dst:
    dst.write(lcoe, 1)

print(
    "LCOE min/mean/max (eligible):",
    np.nanmin(lcoe[eligible]),
    np.nanmean(lcoe[eligible]),
    np.nanmax(lcoe[eligible]),
)


# --------------------------------------------------
# 7) Installable capacity and yearly energy potential
#    based on land-use efficiency (35 and 50 MW/km²)
# --------------------------------------------------
# cell area in km² for 100 m resolution
cell_area_km2 = (DST_RES * DST_RES) / 1e6   # 0.01 km² for 100 m pixels

# land-use efficiency factors from the paper
lf_35 = 35.0   # MW/km² (conservative)
lf_50 = 50.0   # MW/km² (ambitious)

# installable capacity per eligible cell (MW)
P_cell_35 = cell_area_km2 * lf_35
P_cell_50 = cell_area_km2 * lf_50

n_eligible = np.count_nonzero(eligible)

P_tot_35_MW = P_cell_35 * n_eligible
P_tot_50_MW = P_cell_50 * n_eligible

print("Number of eligible cells:", n_eligible)
print("Installable capacity (35 MW/km²):", P_tot_35_MW, "MW")
print("Installable capacity (50 MW/km²):", P_tot_50_MW, "MW")

# approximate yearly electricity generation (using mean E_year)
E_year_mean = E_year[eligible].mean()   # kWh/kWp/year
P_tot_35_kW = P_tot_35_MW * 1000.0
P_tot_50_kW = P_tot_50_MW * 1000.0

E_tot_35_GWh = P_tot_35_kW * E_year_mean / 1e6   # GWh/year
E_tot_50_GWh = P_tot_50_kW * E_year_mean / 1e6   # GWh/year

print("Yearly energy (35 MW/km²):", E_tot_35_GWh, "GWh/a")
print("Yearly energy (50 MW/km²):", E_tot_50_GWh, "GWh/a")
