-- EcoImmo France 2026 - Database Initialization
-- PostgreSQL with pgvector extension

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set French locale
SET lc_messages TO 'fr_FR.UTF-8';
SET lc_monetary TO 'fr_FR.UTF-8';
SET lc_numeric TO 'fr_FR.UTF-8';
SET lc_time TO 'fr_FR.UTF-8';

-- Create schema
CREATE SCHEMA IF NOT EXISTS ecoimmo;

-- Properties table (DVF data)
CREATE TABLE IF NOT EXISTS ecoimmo.properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_mutation VARCHAR(255) UNIQUE NOT NULL,
    date_mutation TIMESTAMP NOT NULL,
    nature_mutation VARCHAR(100),
    valeur_fonciere NUMERIC(12, 2),
    code_postal VARCHAR(5) NOT NULL,
    code_commune VARCHAR(5) NOT NULL,
    nom_commune VARCHAR(255),
    type_local VARCHAR(50),
    surface_reelle_bati NUMERIC(10, 2),
    nombre_pieces_principales INTEGER,
    longitude NUMERIC(10, 7),
    latitude NUMERIC(10, 7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DPE diagnostics table (ADEME data)
CREATE TABLE IF NOT EXISTS ecoimmo.dpe_diagnostics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    n_dpe VARCHAR(255) UNIQUE NOT NULL,
    date_etablissement_dpe TIMESTAMP NOT NULL,
    classe_consommation_energie VARCHAR(1) CHECK (classe_consommation_energie IN ('A', 'B', 'C', 'D', 'E', 'F', 'G')),
    classe_estimation_ges VARCHAR(1),
    consommation_energie NUMERIC(10, 2),
    estimation_ges NUMERIC(10, 2),
    code_postal VARCHAR(5) NOT NULL,
    type_batiment VARCHAR(50),
    annee_construction VARCHAR(4),
    surface_habitable NUMERIC(10, 2),
    type_energie_principale_chauffage VARCHAR(50),
    conso_chauffage NUMERIC(10, 2),
    conso_ecs NUMERIC(10, 2),
    conso_refroidissement NUMERIC(10, 2),
    conso_eclairage NUMERIC(10, 2),
    conso_auxiliaires NUMERIC(10, 2),
    is_passoire_thermique BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DPE 2026 recalculations table
CREATE TABLE IF NOT EXISTS ecoimmo.dpe_2026_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dpe_id UUID REFERENCES ecoimmo.dpe_diagnostics(id),
    original_classification VARCHAR(1),
    original_primary_energy NUMERIC(10, 2),
    recalculated_primary_energy NUMERIC(10, 2),
    recalculated_classification VARCHAR(1),
    electricity_conversion_factor NUMERIC(3, 2) DEFAULT 1.9,
    is_passoire_thermique BOOLEAN,
    renovation_urgency VARCHAR(20),
    rental_ban_date TIMESTAMP,
    estimated_energy_cost_annual NUMERIC(10, 2),
    potential_value_loss_percent NUMERIC(5, 2),
    calculation_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User searches (GDPR-compliant, anonymized)
CREATE TABLE IF NOT EXISTS ecoimmo.user_searches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_query JSONB NOT NULL,
    code_postal VARCHAR(5),
    results_count INTEGER,
    ip_address_hashed VARCHAR(64), -- Hashed for privacy
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI insights cache (Mistral AI responses)
CREATE TABLE IF NOT EXISTS ecoimmo.ai_insights_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    response TEXT NOT NULL,
    model_name VARCHAR(50),
    embedding vector(1536), -- For semantic search with pgvector
    ai_transparency_badge BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_properties_code_postal ON ecoimmo.properties(code_postal);
CREATE INDEX idx_properties_date_mutation ON ecoimmo.properties(date_mutation);
CREATE INDEX idx_properties_type_local ON ecoimmo.properties(type_local);
CREATE INDEX idx_properties_geolocation ON ecoimmo.properties(longitude, latitude);

CREATE INDEX idx_dpe_code_postal ON ecoimmo.dpe_diagnostics(code_postal);
CREATE INDEX idx_dpe_classe ON ecoimmo.dpe_diagnostics(classe_consommation_energie);
CREATE INDEX idx_dpe_passoire ON ecoimmo.dpe_diagnostics(is_passoire_thermique) WHERE is_passoire_thermique = TRUE;

CREATE INDEX idx_dpe_2026_recalc ON ecoimmo.dpe_2026_calculations(dpe_id);
CREATE INDEX idx_user_searches_created ON ecoimmo.user_searches(created_at);

-- Vector similarity index for AI semantic search
CREATE INDEX idx_ai_insights_embedding ON ecoimmo.ai_insights_cache USING ivfflat (embedding vector_cosine_ops);

-- Data retention policy (GDPR compliance)
-- Auto-delete user searches older than 90 days
CREATE OR REPLACE FUNCTION ecoimmo.delete_old_searches()
RETURNS void AS $$
BEGIN
    DELETE FROM ecoimmo.user_searches
    WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (requires pg_cron extension, optional)
-- SELECT cron.schedule('cleanup-searches', '0 2 * * *', 'SELECT ecoimmo.delete_old_searches()');

-- Grant permissions
GRANT USAGE ON SCHEMA ecoimmo TO ecoimmo;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ecoimmo TO ecoimmo;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ecoimmo TO ecoimmo;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'EcoImmo France 2026 database initialized successfully!';
    RAISE NOTICE 'Schema: ecoimmo';
    RAISE NOTICE 'Tables created: 6';
    RAISE NOTICE 'pgvector extension enabled';
END $$;
