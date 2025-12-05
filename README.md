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

## Core Methodology Steps

### 1. Initialization & Region Definition

- Define spatial reference system (CRS) 
- Set output resolution: 100m × 100m pixels
- Define geographic area of interest (Südoststeiermark)
- Create initial region mask (Boolean raster covering entire area)

### 2. Data Acquisition

#### Vector Data:
- Power transmission lines
- Roads network
- Railways
- Airports
- Urban areas
- Industrial areas
- Protected areas (Natura 2000 equivalent for Austria)
- Forest areas (deciduous, coniferous, mixed)
- Administrativ boarders [data.gv.at (https://www.data.gv.at/datasets/aa22cd20-395f-11e2-81c1-0800200c9a66?locale=de)
]

#### Raster Data:
- Digital Elevation Model (DEM) [SRTM (NASA Shuttle Radar Topography Mission (SRTM)(2013). Shuttle Radar Topography Mission (SRTM) Global.  Distributed by OpenTopography.  https://doi.org/10.5069/G9445JDF. Accessed 2025-12-04)]
- Land cover classification (CORINE Land Cover or equivalent)


### 3. Data Preprocessing

For each dataset:
- Clip to study area boundaries
- Reproject to common CRS
- Ensure consistent resolution (100m)
- Convert vector to raster where needed
- Apply buffer distances where specified


### 4. Exclusion Constraint Application

Apply 20 constraints iteratively (from Table 1):

| Constraint | Buffer Distance |
|------------|----------------|
| Power transmission lines | 120m 
| Roads | 100m |
| Railways | 100m |
| Airports | 5000m | 
| Urban areas | 500m | 
| Industrial areas | 500m | 
| Lakes | 0m |
| Forests (all types) | 0m | 
| Slopes > 30° | 0m | 


### 5. Boolean Matrix Operations

- Start with all pixels = 1 (available)
- For each constraint:
  - Create Boolean mask (1 = exclude, 0 = available)
  - Apply logical AND operation to region mask
  - Update cumulative exclusion map
- Final output: Binary raster (1 = eligible, 0 = excluded)



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



### LCOE Calculation Framework
Following Benalcazar et al. (2024), LCOE is calculated as:
```
LCOE = (CAPEX + OPEX) / Lifetime Energy Production

Where:
CAPEX = Hardware + Soft Costs + Installation Costs
OPEX = O&M Costs (as % of installation costs)
```




### Key Python Libraries
- geopandas: Vector geospatial data processing
- rasterio: Raster data processing
- pandas/numpy: Data analysis
- Kepler: Visualization

## Data Management


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

