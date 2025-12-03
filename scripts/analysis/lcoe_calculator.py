"""
LCOE Calculator for Austria PV Assessment
Implements the LCOE formula from Benalcazar et al. (2024) with Austrian parameters
"""

import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config import TECHNO_ECONOMIC_PARAMS

class LCOECalculator:
    """Calculates Levelized Cost of Electricity for utility-scale PV systems"""

    def __init__(self, params=None):
        self.params = params or TECHNO_ECONOMIC_PARAMS

    def calculate_capex(self, hardware_cost=None, soft_cost_factor=0.5, installation_factor=0.2):
        """
        Calculate Capital Expenditures following Eq. (2) from the paper

        CAPEX = Hardware + Soft Costs + Installation Costs
        Soft costs = (Hardware + Installation) * factor
        """
        H = hardware_cost or self.params['hardware_cost_eur_kw']

        # Conservative estimates based on IRENA cost breakdown
        soft_costs = (H + H * installation_factor) * soft_cost_factor
        installation_costs = H * installation_factor

        capex = H + soft_costs + installation_costs

        return {
            'total_capex': capex,
            'hardware': H,
            'soft_costs': soft_costs,
            'installation': installation_costs
        }

    def calculate_capital_recovery_factor(self, discount_rate=None, lifetime=None):
        """
        Calculate Capital Recovery Factor (CRF) - Eq. (4)

        CRF = i * (1+i)^N / ((1+i)^N - 1)
        """
        i = (discount_rate or self.params['discount_rate_percent']) / 100
        N = lifetime or self.params['project_lifetime_years']

        crf = i * (1 + i)**N / ((1 + i)**N - 1)

        return crf

    def calculate_opex(self, installation_costs, o_and_m_rate=None):
        """
        Calculate Operating Expenditures - Eq. (3)

        OPEX = θ * Installation Costs
        """
        theta = (o_and_m_rate or self.params['o_and_m_percent']) / 100

        opex_annual = theta * installation_costs

        return opex_annual

    def calculate_lcoe(self, yearly_energy_production_kwh, hardware_cost=None,
                      discount_rate=None, lifetime=None, o_and_m_rate=None):
        """
        Calculate Levelized Cost of Electricity - Eq. (5)

        LCOE = (CAPEX * CRF + OPEX) / Yearly Energy Production
        """
        # Calculate CAPEX components
        capex_breakdown = self.calculate_capex(hardware_cost)
        capex_total = capex_breakdown['total_capex']

        # Calculate CRF
        crf = self.calculate_capital_recovery_factor(discount_rate, lifetime)

        # Calculate annual OPEX
        opex_annual = self.calculate_opex(capex_breakdown['installation'], o_and_m_rate)

        # Calculate LCOE
        annualized_capex = capex_total * crf
        total_annual_costs = annualized_capex + opex_annual

        lcoe = total_annual_costs / yearly_energy_production_kwh

        return {
            'lcoe_eur_kwh': lcoe,
            'breakdown': {
                'capex_total': capex_total,
                'capex_annualized': annualized_capex,
                'opex_annual': opex_annual,
                'total_annual_costs': total_annual_costs,
                'yearly_production_kwh': yearly_energy_production_kwh,
                'crf': crf
            }
        }

    def calculate_for_austria_regions(self, regional_production_factors=None):
        """
        Calculate LCOE for different Austrian regions based on solar irradiance
        """

        # Austria regional solar production factors (kWh/kWp/year)
        # Based on Global Solar Atlas data for Austria
        if regional_production_factors is None:
            regional_production_factors = {
                'AT11': 1100,  # Eastern Austria
                'AT12': 1050,  # Lower Austria
                'AT13': 1020,  # Vienna
                'AT21': 1080,  # Carinthia
                'AT22': 1120,  # Styria
                'AT31': 1040,  # Upper Austria
                'AT32': 1030,  # Salzburg
                'AT33': 1180,  # Tyrol
                'AT34': 1150   # Vorarlberg
            }

        results = {}

        # Assume 1 kWp system for LCOE calculation
        system_capacity_kw = 1

        for region, production_factor in regional_production_factors.items():
            yearly_production = system_capacity_kw * production_factor

            lcoe_result = self.calculate_lcoe(yearly_production)

            results[region] = {
                'region_name': TECHNO_ECONOMIC_PARAMS.get('austria_regions', {}).get(region, region),
                'solar_production_factor': production_factor,
                'yearly_production_kwh': yearly_production,
                'lcoe_eur_kwh': lcoe_result['lcoe_eur_kwh']
            }

        return results

def main():
    """Demonstrate LCOE calculation with Austrian parameters"""

    calculator = LCOECalculator()

    print("Austria PV LCOE Calculator")
    print("=" * 40)
    print(f"Parameters: {TECHNO_ECONOMIC_PARAMS}")
    print()

    # Example calculation for a 1 kWp system
    example_production = 1100  # kWh/year (typical for Austria)
    lcoe_result = calculator.calculate_lcoe(example_production)

    print("Example LCOE Calculation (1 kWp system, 1100 kWh/year):")
    print(".4f")
    print()
    print("Cost Breakdown:")
    print(".2f")
    print(".2f")
    print(".2f")
    print(".2f")
    print()

    # Regional calculations
    regional_results = calculator.calculate_for_austria_regions()

    print("LCOE by Austrian NUTS-2 Region:")
    print("-" * 50)
    for region, data in regional_results.items():
        print("6s")

    print()
    print(".4f")

if __name__ == "__main__":
    main()
