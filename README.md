# GIS-based Assessment of Utility-Scale Photovoltaic Potential in Austria

This project adapts and implements the methodology from "A GIS-based method for assessing the economics of utility-scale photovoltaic systems" (Benalcazar et al., 2024) to assess solar photovoltaic potential in Austria.

## Project Overview

### Original Methodology
The original study developed a comprehensive GIS-based framework to assess land eligibility and techno-economic potential of utility-scale photovoltaic (PV) systems in Poland. The approach combines:
- **Land eligibility analysis** using 20 exclusion criteria to identify suitable areas
- **Techno-economic assessment** using Levelized Cost of Electricity (LCOE) calculations
- **Spatial analysis** at 100m resolution across NUTS-2 administrative regions

### Adaptation for a Südoststeiermark a Bezirk (County)of Styria
We adapt this methodology to Südoststeiermerk's context.

## Project Goals

1. **Land Eligibility Mapping**: Identify suitable areas for utility-scale PV installations across Austria using spatially-explicit exclusion criteria
2. **Capacity and Generation Potential**: Estimate installable PV capacity and electricity generation potential at 100m resolution
3. **Economic Assessment**: Calculate Levelized Cost of Electricity (LCOE) considering Austria-specific techno-economic parameters
5. **Visualize the generated Results**: Generate visualizations of our results...

## Methodology Adaptation

### Land Eligibility Criteria
Adapted from the original 20 criteria to Austrian context:
- **Physical constraints**: slope (>30°), water bodies
- **Environmental protection**: Natura 2000 sites, habitat protection areas
- **Infrastructure**: Power lines, roads, railways, airports
- **Land use**: Urban/industrial areas, forests, agricultural lands

### Techno-Economic Parameters
Austria-specific calibration of:
- Hardware costs (€/kW)
- Installation and soft costs
- Discount rates
- Operational and maintenance costs
- Land use efficiency scenarios

### Data Sources
- **Land cover**: CORINE Land Cover 2018 (Copernicus)
- **Elevation/Slope**: SRTM (NASA Shuttle Radar Topography Mission (SRTM)(2013). Shuttle Radar Topography Mission (SRTM) Global.  Distributed by OpenTopography.  https://doi.org/10.5069/G9445JDF. Accessed 2025-12-04)
- **Protected areas**: Natura 2000
- **Solar irradiation**: Global Solar Atlas (Solargis)
- **Infrastructure**: OpenStreetMap
- **Administrative boundaries**: data.gv.at (https://www.data.gv.at/datasets/aa22cd20-395f-11e2-81c1-0800200c9a66?locale=de)

## Project Structure

```
├── data/
│   ├── raw/                 # Raw geospatial data
│   ├── processed/           # Processed datasets
│   └── results/             # Analysis outputs
├── scripts/
│   ├── preprocessing/       # Data acquisition and preprocessing
│   ├── analysis/            # Core GIS analysis scripts
│   └── visualization/       # Results visualization
├── docs/
│   ├── methodology/         # Detailed methodology documentation
│   └── references/          # Reference materials
├── notebooks/               # Jupyter notebooks for analysis
├── config.py                # Project configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Implementation Roadmap

### Phase 1: Project Setup and Data Acquisition
- [x] Create project structure
- [ ] Set up development environment
- [ ] Identify and acquire geospatial data sources
- [ ] Implement data download scripts

### Phase 2: Land Eligibility Analysis
- [ ] Develop exclusion criteria processing pipeline
- [ ] Implement GIS-based land suitability analysis
- [ ] Validate exclusion criteria for Austrian context
- [ ] Generate land eligibility maps

### Phase 3: Techno-Economic Assessment
- [ ] Calibrate techno-economic parameters for Austria
- [ ] Implement LCOE calculation framework
- [ ] Integrate solar resource data
- [ ] Perform capacity and generation potential analysis

### Phase 4: Results Analysis and Visualization
- [ ] Create regional summary statistics
- [ ] Develop interactive maps and visualizations
- [ ] Generate policy-relevant insights
- [ ] Produce final report and recommendations

## Key Technical Components

### GIS Processing Pipeline
1. **Data Preprocessing**: Coordinate system alignment, clipping to Südoststeiermark boundaries
2. **Exclusion Application**: Sequential application (number of) land eligibility criteria
3. **Solar Resource Integration**: Overlay with solar irradiation data
4. **Economic Calculations**: LCOE computation for eligible areas

### LCOE Calculation Framework
Following Benalcazar et al. (2024), LCOE is calculated as:
```
LCOE = (CAPEX + OPEX) / Lifetime Energy Production

Where:
CAPEX = Hardware + Soft Costs + Installation Costs
OPEX = O&M Costs (as % of installation costs)
```

### Quality Assurance
- **Spatial Resolution**: 100m × 100m grid cells
- **Coordinate System**: ETRS89-extended / LAEA Europe (EPSG:32633)
- **Data Validation**: Cross-checking against official statistics
- **Uncertainty Analysis**: Sensitivity testing of key parameters

## Expected Outputs

1. **Land Eligibility Maps**: Spatial distribution of suitable areas
2. **Capacity Potential Maps**: Installable PV capacity by region
3. **LCOE Maps**: Economic viability assessment
4. **Regional Reports**: Detailed analysis for each NUTS-2 region
5. **Policy Brief**: Key findings and recommendations

## Dependencies and Requirements

### Software Requirements
- Python 3.8+
- QGIS 3.28+ (for GIS operations)
- GDAL/OGR (for geospatial data processing)

### Key Python Libraries
- geopandas: Vector geospatial data processing
- rasterio: Raster data processing
- pandas/numpy: Data analysis
- Kepler: Visualization
- requests: Data acquisition

## Data Management

### Data Sources and Licensing
- **Open Data**: CORINE Land Cover, SRTM DEM, Bezirksgrenzen Steiermark
- **Restricted Access**: Some datasets may require registration
- **Licensing**: Ensure compliance with data provider terms


## Team and Collaboration

### Development Workflow
1. **Version Control**: Git-based collaboration
2. **Documentation**: Comprehensive code documentation

### Quality Standards
- **Reproducibility**: Documented methodology and parameters
- **Transparency**: Open source code and data sources


## References

1. Benalcazar, P., Komorowska, A., & Kamiński, J. (2024). A GIS-based method for assessing the economics of utility-scale photovoltaic systems. *Applied Energy*, 353, 122044.

2. IRENA. (2022). Renewable power generation costs in 2021.

3. European Commission. (2022). EU solar energy strategy.

