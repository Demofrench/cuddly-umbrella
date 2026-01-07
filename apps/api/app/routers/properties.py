"""
Properties Router
=================
Endpoints for property search and DPE 2026 analysis
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.main import get_data_fetcher
from app.services.french_gov_data_fetcher import FrenchGovDataFetcher
from app.services.dpe_2026_calculator import DPE2026Calculator, EnergyConsumption


router = APIRouter()


class PropertySearchRequest(BaseModel):
    """Property search parameters"""
    code_postal: str = Field(..., description="Postal code (e.g., '75015')")
    type_local: Optional[str] = Field(None, description="Property type: 'Maison' or 'Appartement'")
    date_min: Optional[datetime] = Field(None, description="Minimum transaction date")
    date_max: Optional[datetime] = Field(None, description="Maximum transaction date")
    limit: int = Field(100, ge=1, le=500, description="Maximum results")


class DPE2026AnalysisRequest(BaseModel):
    """Request for DPE 2026 recalculation"""
    original_dpe_class: str = Field(..., pattern="^[A-G]$", description="Original DPE class")
    original_primary_energy: float = Field(..., gt=0, description="Original primary energy (kWh EP/m²/year)")
    heating_kwh: float = Field(..., ge=0)
    hot_water_kwh: float = Field(..., ge=0)
    cooling_kwh: float = Field(0, ge=0)
    lighting_kwh: float = Field(0, ge=0)
    auxiliary_kwh: float = Field(0, ge=0)
    electricity_percentage: float = Field(..., ge=0, le=1, description="Percentage of energy from electricity")
    gas_percentage: float = Field(0, ge=0, le=1)
    fuel_oil_percentage: float = Field(0, ge=0, le=1)
    wood_percentage: float = Field(0, ge=0, le=1)
    surface_m2: float = Field(..., gt=0, description="Property surface (m²)")
    is_rental_property: bool = Field(False, description="Is this a rental property?")


@router.get("/search")
async def search_properties(
    code_postal: str = Query(..., description="Postal code"),
    type_local: Optional[str] = Query(None, description="Property type"),
    limit: int = Query(100, ge=1, le=500),
    fetcher: FrenchGovDataFetcher = Depends(get_data_fetcher)
):
    """
    Search properties with DVF + DPE cross-reference

    Returns property transactions enriched with energy performance data.
    """
    try:
        enriched_properties = await fetcher.cross_reference_dvf_dpe(
            code_postal=code_postal,
            date_range_days=365
        )

        # Filter by type if specified
        if type_local:
            enriched_properties = [
                p for p in enriched_properties
                if p['transaction']['type_local'] == type_local
            ]

        return {
            "total": len(enriched_properties),
            "properties": enriched_properties[:limit],
            "metadata": {
                "code_postal": code_postal,
                "with_dpe": len([p for p in enriched_properties if p['dpe']]),
                "without_dpe": len([p for p in enriched_properties if not p['dpe']])
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/analyze-dpe-2026")
async def analyze_dpe_2026(request: DPE2026AnalysisRequest):
    """
    Recalculate DPE with 2026 regulatory updates

    Applies the new 1.9 electricity conversion factor and determines:
    - Updated DPE classification
    - Passoire Thermique status
    - Rental ban dates (Loi Climat 2026)
    - Financial impact estimation
    - Priority renovation recommendations
    """
    try:
        calculator = DPE2026Calculator(enable_ai_transparency=True)

        # Build energy consumption
        consumption = EnergyConsumption(
            heating_kwh=request.heating_kwh,
            hot_water_kwh=request.hot_water_kwh,
            cooling_kwh=request.cooling_kwh,
            lighting_kwh=request.lighting_kwh,
            auxiliary_kwh=request.auxiliary_kwh
        )

        # Build energy mix
        other_sources = {}
        if request.gas_percentage > 0:
            other_sources['gas'] = request.gas_percentage
        if request.fuel_oil_percentage > 0:
            other_sources['fuel_oil'] = request.fuel_oil_percentage
        if request.wood_percentage > 0:
            other_sources['wood'] = request.wood_percentage

        # Calculate
        result = calculator.calculate_full_dpe_2026(
            original_dpe_class=request.original_dpe_class,
            original_primary_energy=request.original_primary_energy,
            final_energy_consumption=consumption,
            electricity_percentage=request.electricity_percentage,
            other_energy_sources=other_sources,
            surface_m2=request.surface_m2,
            is_rental_property=request.is_rental_property
        )

        return {
            "original": {
                "classification": result.original_classification.value,
                "primary_energy": result.original_primary_energy
            },
            "recalculated_2026": {
                "classification": result.recalculated_classification.value,
                "primary_energy": result.recalculated_primary_energy,
                "change": result.original_primary_energy - result.recalculated_primary_energy
            },
            "regulatory_status": {
                "is_passoire_thermique": result.is_passoire_thermique,
                "renovation_urgency": result.renovation_urgency.value,
                "rental_ban_date": result.rental_ban_date.isoformat() if result.rental_ban_date else None
            },
            "financial_impact": {
                "estimated_annual_energy_cost_eur": result.estimated_energy_cost_annual,
                "potential_value_loss_percent": result.potential_value_loss_percent,
                "renovation_cost_range_eur": {
                    "min": result.estimated_renovation_cost_range[0],
                    "max": result.estimated_renovation_cost_range[1]
                }
            },
            "recommendations": {
                "priority_renovations": result.priority_renovations
            },
            "compliance": {
                "ai_transparency_badge": result.ai_transparency_badge,
                "human_verification_required": result.human_verification_required,
                "calculation_metadata": result.calculation_metadata
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@router.get("/passoire-thermique-map")
async def passoire_thermique_map(
    code_postal: str = Query(..., description="Postal code"),
    fetcher: FrenchGovDataFetcher = Depends(get_data_fetcher)
):
    """
    Generate Passoire Thermique density map for a postal code

    Useful for visualizing energy-poor housing distribution.
    """
    diagnostics = await fetcher.fetch_dpe_diagnostics(
        code_postal=code_postal,
        limit=500
    )

    # Count by classification
    classification_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0}
    for dpe in diagnostics:
        if dpe.classe_consommation_energie in classification_counts:
            classification_counts[dpe.classe_consommation_energie] += 1

    passoire_count = classification_counts["F"] + classification_counts["G"]
    total = len(diagnostics)

    return {
        "code_postal": code_postal,
        "total_properties": total,
        "passoire_thermique_count": passoire_count,
        "passoire_percentage": round(passoire_count / total * 100, 1) if total > 0 else 0,
        "classification_distribution": classification_counts,
        "risk_level": "high" if passoire_count / total > 0.3 else "medium" if passoire_count / total > 0.15 else "low"
    }
