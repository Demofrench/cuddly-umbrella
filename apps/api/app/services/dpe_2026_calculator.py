"""
DPE 2026 Calculator Service
============================
Regulatory Compliance Module for French Energy Performance Diagnostics

CRITICAL 2026 UPDATE:
- Implements new electricity-to-primary-energy conversion factor: 1.9 (decreased from 2.3)
- Recalculates 'Passoire Thermique' risks based on Decree No. 2026-01
- Complies with EU Energy Performance of Buildings Directive (EPBD) 2024
- Integrates EU AI Act transparency requirements

Author: EcoImmo France Architecture Team
Date: January 2026
Regulatory Framework: Loi Climat et Résilience + EU AI Act
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
import logging

# Configure logger
logger = logging.getLogger(__name__)


class DPEClassification(str, Enum):
    """DPE Energy Performance Classifications (A-G scale)"""
    A = "A"  # ≤ 70 kWh/m²/year (Excellent)
    B = "B"  # 71-110 kWh/m²/year (Good)
    C = "C"  # 111-180 kWh/m²/year (Average)
    D = "D"  # 181-250 kWh/m²/year (Mediocre)
    E = "E"  # 251-330 kWh/m²/year (Poor)
    F = "F"  # 331-420 kWh/m²/year (Very Poor - Passoire Thermique)
    G = "G"  # > 420 kWh/m²/year (Extremely Poor - Passoire Thermique)


class RenovationUrgency(str, Enum):
    """Renovation urgency based on Loi Climat 2026 compliance"""
    COMPLIANT = "compliant"  # A-E: Rentable until 2034
    WARNING = "warning"  # E: Rental ban from 2034
    URGENT = "urgent"  # F: Rental ban from 2028
    CRITICAL = "critical"  # G: Already banned since 2025


@dataclass
class EnergyConsumption:
    """Energy consumption breakdown by source"""
    heating_kwh: float
    hot_water_kwh: float
    cooling_kwh: float
    lighting_kwh: float
    auxiliary_kwh: float  # Ventilation, pumps, etc.

    @property
    def total_final_energy(self) -> float:
        """Total final energy consumption (kWh/m²/year)"""
        return (
            self.heating_kwh +
            self.hot_water_kwh +
            self.cooling_kwh +
            self.lighting_kwh +
            self.auxiliary_kwh
        )


@dataclass
class DPE2026Result:
    """Complete DPE 2026 calculation result"""
    # Original ADEME data
    original_classification: DPEClassification
    original_primary_energy: float  # kWh EP/m²/year (old 2.3 factor)

    # Recalculated with 2026 factor
    recalculated_primary_energy: float  # kWh EP/m²/year (new 1.9 factor)
    recalculated_classification: DPEClassification

    # Regulatory status
    is_passoire_thermique: bool
    renovation_urgency: RenovationUrgency
    rental_ban_date: Optional[datetime]

    # Financial impact
    estimated_energy_cost_annual: float  # EUR/year
    potential_value_loss_percent: float  # % depreciation

    # AI Act compliance
    calculation_metadata: Dict
    ai_transparency_badge: bool = True
    human_verification_required: bool = False

    # Renovation recommendations
    priority_renovations: List[str]
    estimated_renovation_cost_range: tuple  # (min, max) in EUR


class DPE2026Calculator:
    """
    Main calculator implementing the 2026 regulatory framework

    Key Changes:
    - Electricity conversion factor: 2.3 → 1.9 (Jan 2026 decree)
    - Gas/Fuel oil remains at 1.0 (unchanged)
    - District heating: case-by-case based on energy mix
    """

    # Regulatory constants
    ELECTRICITY_FACTOR_2026 = 1.9  # New value (down from 2.3)
    ELECTRICITY_FACTOR_PRE_2026 = 2.3  # Historical value
    GAS_FACTOR = 1.0
    FUEL_OIL_FACTOR = 1.0
    WOOD_FACTOR = 0.6

    # DPE classification thresholds (kWh EP/m²/year)
    DPE_THRESHOLDS = {
        DPEClassification.A: (0, 70),
        DPEClassification.B: (71, 110),
        DPEClassification.C: (111, 180),
        DPEClassification.D: (181, 250),
        DPEClassification.E: (251, 330),
        DPEClassification.F: (331, 420),
        DPEClassification.G: (421, float('inf'))
    }

    # Loi Climat rental ban dates
    RENTAL_BAN_DATES = {
        DPEClassification.G: datetime(2025, 1, 1),  # Already banned
        DPEClassification.F: datetime(2028, 1, 1),
        DPEClassification.E: datetime(2034, 1, 1),
    }

    # Average energy costs (EUR/kWh) - 2026 rates
    ENERGY_COSTS = {
        'electricity': 0.2516,  # TTC with TURPE
        'gas': 0.1121,
        'fuel_oil': 0.1450,
        'wood': 0.0650
    }

    def __init__(self, enable_ai_transparency: bool = True):
        """
        Initialize calculator with EU AI Act compliance settings

        Args:
            enable_ai_transparency: Include AI transparency badges (EU AI Act)
        """
        self.enable_ai_transparency = enable_ai_transparency
        logger.info(f"DPE2026Calculator initialized with electricity factor {self.ELECTRICITY_FACTOR_2026}")

    def classify_energy_performance(self, primary_energy_kwh: float) -> DPEClassification:
        """
        Classify property based on primary energy consumption

        Args:
            primary_energy_kwh: Primary energy consumption (kWh EP/m²/year)

        Returns:
            DPE classification (A-G)
        """
        for classification, (min_val, max_val) in self.DPE_THRESHOLDS.items():
            if min_val <= primary_energy_kwh <= max_val:
                return classification
        return DPEClassification.G  # Fallback

    def recalculate_with_2026_factor(
        self,
        final_energy_consumption: EnergyConsumption,
        electricity_percentage: float,
        other_energy_sources: Dict[str, float]  # {'gas': 0.3, 'wood': 0.1}
    ) -> float:
        """
        Recalculate primary energy using the new 2026 conversion factor

        Args:
            final_energy_consumption: Breakdown of energy usage
            electricity_percentage: Percentage of energy from electricity (0-1)
            other_energy_sources: Dictionary of other sources and their percentages

        Returns:
            Recalculated primary energy (kWh EP/m²/year)
        """
        total_final = final_energy_consumption.total_final_energy

        # Calculate weighted conversion factor
        weighted_factor = 0.0

        # Electricity component
        weighted_factor += electricity_percentage * self.ELECTRICITY_FACTOR_2026

        # Other energy sources
        for source, percentage in other_energy_sources.items():
            if source == 'gas':
                weighted_factor += percentage * self.GAS_FACTOR
            elif source == 'fuel_oil':
                weighted_factor += percentage * self.FUEL_OIL_FACTOR
            elif source == 'wood':
                weighted_factor += percentage * self.WOOD_FACTOR

        # Apply conversion
        primary_energy = total_final * weighted_factor

        logger.info(
            f"Recalculated: {total_final:.2f} kWh final → "
            f"{primary_energy:.2f} kWh EP (factor: {weighted_factor:.2f})"
        )

        return primary_energy

    def calculate_renovation_urgency(
        self,
        classification: DPEClassification,
        is_rental_property: bool
    ) -> RenovationUrgency:
        """
        Determine renovation urgency based on Loi Climat 2026

        Args:
            classification: Current DPE classification
            is_rental_property: Whether the property is for rental

        Returns:
            Renovation urgency level
        """
        if not is_rental_property:
            return RenovationUrgency.COMPLIANT

        if classification == DPEClassification.G:
            return RenovationUrgency.CRITICAL
        elif classification == DPEClassification.F:
            return RenovationUrgency.URGENT
        elif classification == DPEClassification.E:
            return RenovationUrgency.WARNING
        else:
            return RenovationUrgency.COMPLIANT

    def estimate_energy_costs(
        self,
        final_energy_kwh: float,
        surface_m2: float,
        energy_mix: Dict[str, float]
    ) -> float:
        """
        Estimate annual energy costs

        Args:
            final_energy_kwh: Final energy consumption (kWh/m²/year)
            surface_m2: Property surface area (m²)
            energy_mix: Energy source distribution

        Returns:
            Estimated annual cost (EUR/year)
        """
        total_cost = 0.0
        total_consumption = final_energy_kwh * surface_m2

        for source, percentage in energy_mix.items():
            source_consumption = total_consumption * percentage
            cost_per_kwh = self.ENERGY_COSTS.get(source, 0.15)  # Default fallback
            total_cost += source_consumption * cost_per_kwh

        return round(total_cost, 2)

    def calculate_value_depreciation(
        self,
        classification: DPEClassification,
        is_rental_property: bool
    ) -> float:
        """
        Estimate property value depreciation based on energy performance

        Based on Notaires de France 2025 study:
        - F/G properties: 10-18% value loss vs. D classification
        - E properties: 5-8% value loss
        - Rental ban amplifies depreciation

        Args:
            classification: DPE classification
            is_rental_property: Whether property is for rental

        Returns:
            Estimated depreciation percentage (0-100)
        """
        base_depreciation = {
            DPEClassification.A: 0.0,
            DPEClassification.B: 0.0,
            DPEClassification.C: 0.0,
            DPEClassification.D: 0.0,
            DPEClassification.E: 6.5,
            DPEClassification.F: 12.0,
            DPEClassification.G: 16.0
        }

        depreciation = base_depreciation.get(classification, 0.0)

        # Amplify for rental properties facing ban
        if is_rental_property and classification in [DPEClassification.F, DPEClassification.G]:
            depreciation *= 1.25  # 25% additional depreciation

        return round(depreciation, 1)

    def generate_renovation_priorities(
        self,
        classification: DPEClassification,
        consumption: EnergyConsumption
    ) -> List[str]:
        """
        Generate prioritized renovation recommendations

        Args:
            classification: Current DPE classification
            consumption: Energy consumption breakdown

        Returns:
            List of prioritized renovation actions
        """
        priorities = []

        # Heating is usually the biggest lever
        if consumption.heating_kwh > 150:
            priorities.append("Isolation thermique (combles, murs, planchers)")
            priorities.append("Remplacement du système de chauffage (pompe à chaleur)")

        # Hot water optimization
        if consumption.hot_water_kwh > 50:
            priorities.append("Chauffe-eau thermodynamique ou solaire")

        # Windows for F/G properties
        if classification in [DPEClassification.F, DPEClassification.G]:
            priorities.append("Remplacement des fenêtres (double/triple vitrage)")
            priorities.append("Installation d'une VMC double flux")

        # Renewable energy
        priorities.append("Panneaux solaires photovoltaïques (autoconsommation)")

        return priorities[:5]  # Top 5 priorities

    def estimate_renovation_costs(
        self,
        classification: DPEClassification,
        surface_m2: float
    ) -> tuple:
        """
        Estimate renovation cost range based on surface and classification

        Based on ANAH 2025 averages:
        - Light renovation (E→D): 150-250 EUR/m²
        - Medium renovation (F→C): 300-500 EUR/m²
        - Heavy renovation (G→B): 500-800 EUR/m²

        Args:
            classification: Current DPE classification
            surface_m2: Property surface area

        Returns:
            (min_cost, max_cost) tuple in EUR
        """
        cost_per_m2 = {
            DPEClassification.E: (150, 250),
            DPEClassification.F: (300, 500),
            DPEClassification.G: (500, 800)
        }

        if classification not in cost_per_m2:
            return (0, 0)  # No urgent renovation needed

        min_rate, max_rate = cost_per_m2[classification]
        return (
            int(min_rate * surface_m2),
            int(max_rate * surface_m2)
        )

    def calculate_full_dpe_2026(
        self,
        original_dpe_class: str,
        original_primary_energy: float,
        final_energy_consumption: EnergyConsumption,
        electricity_percentage: float,
        other_energy_sources: Dict[str, float],
        surface_m2: float,
        is_rental_property: bool = False
    ) -> DPE2026Result:
        """
        Complete DPE 2026 recalculation with regulatory compliance

        This is the main public method that orchestrates the full calculation.

        Args:
            original_dpe_class: Original ADEME classification (A-G)
            original_primary_energy: Original primary energy (kWh EP/m²/year)
            final_energy_consumption: Detailed consumption breakdown
            electricity_percentage: % of energy from electricity (0-1)
            other_energy_sources: Other energy sources and percentages
            surface_m2: Property surface area (m²)
            is_rental_property: Whether property is for rental

        Returns:
            Complete DPE2026Result with all calculations and recommendations
        """
        logger.info(f"Starting DPE 2026 calculation for {surface_m2}m² property")

        # Step 1: Recalculate with new 2026 factor
        recalculated_primary = self.recalculate_with_2026_factor(
            final_energy_consumption,
            electricity_percentage,
            other_energy_sources
        )

        # Step 2: Reclassify
        original_class = DPEClassification(original_dpe_class)
        recalculated_class = self.classify_energy_performance(recalculated_primary)

        # Step 3: Determine passoire thermique status
        is_passoire = recalculated_class in [DPEClassification.F, DPEClassification.G]

        # Step 4: Calculate renovation urgency
        urgency = self.calculate_renovation_urgency(recalculated_class, is_rental_property)

        # Step 5: Determine rental ban date
        rental_ban = None
        if is_rental_property and recalculated_class in self.RENTAL_BAN_DATES:
            rental_ban = self.RENTAL_BAN_DATES[recalculated_class]

        # Step 6: Financial estimations
        energy_mix = {'electricity': electricity_percentage, **other_energy_sources}
        annual_cost = self.estimate_energy_costs(
            final_energy_consumption.total_final_energy,
            surface_m2,
            energy_mix
        )
        value_loss = self.calculate_value_depreciation(recalculated_class, is_rental_property)

        # Step 7: Renovation recommendations
        priorities = self.generate_renovation_priorities(
            recalculated_class,
            final_energy_consumption
        )
        cost_range = self.estimate_renovation_costs(recalculated_class, surface_m2)

        # Step 8: Build metadata (AI Act compliance)
        metadata = {
            'calculation_date': datetime.now().isoformat(),
            'electricity_factor_used': self.ELECTRICITY_FACTOR_2026,
            'regulatory_framework': 'Loi Climat et Résilience 2026 + EU EPBD 2024',
            'methodology': 'DPE 3CL-2021 (updated Jan 2026)',
            'data_sources': ['ADEME DPE API', 'DVF Gouv'],
            'confidence_level': 'high' if electricity_percentage > 0.8 else 'medium'
        }

        # Step 9: Determine if human verification needed (EU AI Act Art. 14)
        human_verification = (
            is_passoire and
            is_rental_property and
            urgency in [RenovationUrgency.URGENT, RenovationUrgency.CRITICAL]
        )

        result = DPE2026Result(
            original_classification=original_class,
            original_primary_energy=original_primary_energy,
            recalculated_primary_energy=recalculated_primary,
            recalculated_classification=recalculated_class,
            is_passoire_thermique=is_passoire,
            renovation_urgency=urgency,
            rental_ban_date=rental_ban,
            estimated_energy_cost_annual=annual_cost,
            potential_value_loss_percent=value_loss,
            calculation_metadata=metadata,
            ai_transparency_badge=self.enable_ai_transparency,
            human_verification_required=human_verification,
            priority_renovations=priorities,
            estimated_renovation_cost_range=cost_range
        )

        logger.info(
            f"DPE 2026 calculation complete: "
            f"{original_class.value} → {recalculated_class.value} "
            f"({original_primary_energy:.1f} → {recalculated_primary:.1f} kWh EP/m²/year)"
        )

        return result


# Example usage for testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example: Apartment with electric heating (impacted by 2026 factor change)
    calculator = DPE2026Calculator()

    consumption = EnergyConsumption(
        heating_kwh=200.0,
        hot_water_kwh=40.0,
        cooling_kwh=5.0,
        lighting_kwh=10.0,
        auxiliary_kwh=15.0
    )

    result = calculator.calculate_full_dpe_2026(
        original_dpe_class="F",
        original_primary_energy=621.0,  # With old 2.3 factor
        final_energy_consumption=consumption,
        electricity_percentage=0.95,  # 95% electric
        other_energy_sources={'gas': 0.05},
        surface_m2=65.0,
        is_rental_property=True
    )

    print("\n" + "="*60)
    print("DPE 2026 RECALCULATION REPORT")
    print("="*60)
    print(f"Original: {result.original_classification.value} "
          f"({result.original_primary_energy:.1f} kWh EP/m²/year)")
    print(f"Recalculated: {result.recalculated_classification.value} "
          f"({result.recalculated_primary_energy:.1f} kWh EP/m²/year)")
    print(f"Passoire Thermique: {'OUI ⚠️' if result.is_passoire_thermique else 'Non'}")
    print(f"Urgency: {result.renovation_urgency.value.upper()}")
    if result.rental_ban_date:
        print(f"Rental Ban: {result.rental_ban_date.strftime('%d/%m/%Y')}")
    print(f"\nEstimated Annual Energy Cost: {result.estimated_energy_cost_annual:,.0f} EUR")
    print(f"Potential Value Loss: {result.potential_value_loss_percent}%")
    print(f"\nRenovation Cost Range: "
          f"{result.estimated_renovation_cost_range[0]:,}-"
          f"{result.estimated_renovation_cost_range[1]:,} EUR")
    print("\nPriority Renovations:")
    for i, priority in enumerate(result.priority_renovations, 1):
        print(f"  {i}. {priority}")
    print("="*60)
