"""
Configuration file for GIS-based PV potential assessment in Austria
Based on methodology from: Benalcazar et al. (2024) - A GIS-based method for assessing the economics of utility-scale photovoltaic systems
"""

# Project settings
PROJECT_NAME = "Austria PV Potential Assessment"
PROJECT_VERSION = "1.0.0"
AUTHORS = ["Based on GIS Analysis Techniques Course"]

# Spatial settings
EPSG_CODE = 3035  # ETRS89-extended / LAEA Europe
RESOLUTION_METERS = 100  # 100m x 100m grid cells

# Austria NUTS-2 regions
AUSTRIA_NUTS2_REGIONS = {
    'AT11': 'Ostösterreich',
    'AT12': 'Niederösterreich',
    'AT13': 'Wien',
    'AT21': 'Kärnten',
    'AT22': 'Steiermark',
    'AT31': 'Oberösterreich',
    'AT32': 'Salzburg',
    'AT33': 'Tirol',
    'AT34': 'Vorarlberg'
}

# Land eligibility exclusion criteria (adapted from Benalcazar et al., 2024)
EXCLUSION_CRITERIA = {
    'power_lines': {'buffer_m': 120, 'description': 'Power transmission lines'},
    'roads': {'buffer_m': 100, 'description': 'Major roads'},
    'railways': {'buffer_m': 100, 'description': 'Railway lines'},
    'airports': {'buffer_m': 5000, 'description': 'Airports'},
    'urban_areas': {'buffer_m': 500, 'description': 'Urban fabric areas'},
    'industrial_areas': {'buffer_m': 500, 'description': 'Industrial areas'},
    'lakes': {'buffer_m': 0, 'description': 'Lakes and water bodies'},
    'rivers': {'buffer_m': 0, 'description': 'Rivers and streams'},
    'marine_waters': {'buffer_m': 0, 'description': 'Marine waters'},
    'bird_protection': {'buffer_m': 200, 'description': 'Bird protection areas'},
    'habitat_protection': {'buffer_m': 300, 'description': 'Habitat protected areas'},
    'national_parks': {'buffer_m': 300, 'description': 'National parks and reserves'},
    'mixed_forests': {'buffer_m': 0, 'description': 'Mixed forests'},
    'deciduous_forests': {'buffer_m': 0, 'description': 'Deciduous forests'},
    'coniferous_forests': {'buffer_m': 0, 'description': 'Coniferous forests'},
    'high_elevation': {'buffer_m': 0, 'threshold_m': 2000, 'description': 'Elevations > 2000m'},
    'steep_slopes': {'buffer_m': 0, 'threshold_deg': 30, 'description': 'Slopes > 30°'},
    'mineral_sites': {'buffer_m': 0, 'description': 'Mineral extraction sites'},
    'arable_land': {'buffer_m': 0, 'description': 'Non-irrigated arable land'},
    'irrigated_land': {'buffer_m': 0, 'description': 'Permanently irrigated land'}
}

# Techno-economic parameters (calibrated for Austria based on 2023 market conditions)
TECHNO_ECONOMIC_PARAMS = {
    'hardware_cost_eur_kw': 844.6,  # €/kW (IRENA 2023 global average + 3% Austria premium)
    'project_lifetime_years': 25,   # years (unchanged from original study)
    'discount_rate_percent': 4.5,   # % (calibrated for Austrian economic conditions)
    'o_and_m_percent': 1.2,         # % of installation costs (adjusted for Austrian labor costs)
    'land_use_efficiency_mw_km2': [35, 50]  # MW/km² (conservative and optimistic scenarios)
}

# Data sources (to be identified and configured)
DATA_SOURCES = {
    'land_cover': {
        'source': 'Copernicus Land Monitoring Service',
        'url': 'https://land.copernicus.eu/',
        'description': 'CORINE Land Cover 2018'
    },
    'elevation': {
        'source': 'Copernicus Land Monitoring Service',
        'url': 'https://land.copernicus.eu/',
        'description': 'EU-DEM v1.1'
    },
    'protected_areas': {
        'source': 'European Environment Agency',
        'url': 'https://www.eea.europa.eu/',
        'description': 'Natura 2000 and CDDA'
    },
    'solar_irradiation': {
        'source': 'Solargis/Global Solar Atlas',
        'url': 'https://globalsolaratlas.info/',
        'description': 'Global Horizontal Irradiation'
    },
    'infrastructure': {
        'source': 'OpenStreetMap',
        'url': 'https://www.openstreetmap.org/',
        'description': 'Transport and power infrastructure'
    }
}

# Output directories
OUTPUT_DIRS = {
    'figures': 'data/results/figures/',
    'rasters': 'data/results/rasters/',
    'vectors': 'data/results/vectors/',
    'reports': 'data/results/reports/'
}

# Processing settings
PROCESSING = {
    'chunk_size': 1000,  # Process data in chunks to manage memory
    'parallel_processing': True,
    'max_workers': 4
}
