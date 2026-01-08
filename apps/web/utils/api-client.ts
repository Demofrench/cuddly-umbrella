/**
 * API Client for EcoImmo France 2026
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface AIPropertyDoctorRequest {
  photo: File
  property_address: string
  surface_m2: number
  code_postal: string
}

export interface AIPropertyDoctorResponse {
  recommendation: {
    verdict: string
    overall_score: number
    risk_level: string
    opportunity_level: string
  }
  vision_analysis: {
    energy_efficiency_score: number
    detected_features: {
      windows?: {
        glazing_type: 'single' | 'double' | 'triple'
        count: number
      }
      insulation?: {
        quality: 'poor' | 'average' | 'good' | 'excellent'
      }
      heating_system?: {
        type: string
      }
    }
    thermal_risks: string[]
  }
  dpe_2026: {
    original_class: string
    recalculated_class: string
    is_passoire_thermique: boolean
    rental_ban_date?: string
    primary_energy_kwh: number
  }
  valuation: {
    market_value_eur: number
    energy_adjusted_value_eur: number
    adjustment_percentage: number
    undervalued_score: number
  }
  market_forecast: {
    trend_description: string
    forecast_3years: number
    growth_percentage_3y: number
    best_time_to_buy?: string
  }
  action_plan: Array<{
    step: number
    title: string
    description: string
    cost_eur?: number
    timeline_days?: number
    priority: 'high' | 'medium' | 'low'
  }>
  full_report?: string
}

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Analyzes a property using AI Property Doctor
 */
export async function diagnoseProperty(
  request: AIPropertyDoctorRequest
): Promise<AIPropertyDoctorResponse> {
  const formData = new FormData()
  formData.append('photo', request.photo)
  formData.append('property_address', request.property_address)
  formData.append('surface_m2', request.surface_m2.toString())
  formData.append('code_postal', request.code_postal)

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai-doctor/diagnose`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - let the browser set it with boundary
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        response.status,
        errorData.detail || `HTTP Error: ${response.status}`,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError(
        0,
        'Impossible de se connecter à l\'API. Vérifiez que le serveur est démarré.',
        error
      )
    }

    throw new APIError(
      500,
      'Une erreur inattendue s\'est produite',
      error
    )
  }
}

/**
 * Gets demo/example analysis (for testing)
 */
export async function getDemoAnalysis(): Promise<AIPropertyDoctorResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai-doctor/demo`)

  if (!response.ok) {
    throw new APIError(response.status, 'Failed to fetch demo data')
  }

  return await response.json()
}

/**
 * Searches properties by postal code
 */
export async function searchProperties(codePostal: string, limit: number = 100) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/properties/search?code_postal=${codePostal}&limit=${limit}`
  )

  if (!response.ok) {
    throw new APIError(response.status, 'Property search failed')
  }

  return await response.json()
}

/**
 * Gets DPE 2026 analysis for a property
 */
export async function analyzeDPE2026(data: {
  original_dpe_class: string
  original_primary_energy: number
  heating_kwh: number
  hot_water_kwh: number
  electricity_percentage: number
  surface_m2: number
  is_rental_property: boolean
}) {
  const response = await fetch(`${API_BASE_URL}/api/v1/properties/analyze-dpe-2026`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new APIError(response.status, errorData.detail || 'DPE analysis failed')
  }

  return await response.json()
}

/**
 * Health check for the API
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new APIError(response.status, 'Health check failed')
  }

  return await response.json()
}
