"""
French Government Data Fetcher Service
======================================
Handles all interactions with French Government Open Data APIs:
- DVF (Demandes de Valeurs Foncières) - Property transaction data
- ADEME DPE - Energy Performance Diagnostics

Features:
- Redis caching to respect rate limits
- Exponential backoff retry logic
- GDPR-compliant data anonymization
- Async/await for high performance

Author: EcoImmo France Architecture Team
Date: January 2026
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import aiohttp
import redis.asyncio as redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DVFTransaction(BaseModel):
    """Property transaction from DVF database"""
    id_mutation: str
    date_mutation: datetime
    nature_mutation: str  # "Vente", "Vente en l'état futur d'achèvement", etc.
    valeur_fonciere: float  # EUR
    adresse_numero: Optional[str]
    adresse_nom_voie: Optional[str]
    code_postal: str
    code_commune: str
    nom_commune: str
    type_local: str  # "Maison", "Appartement", etc.
    surface_reelle_bati: Optional[float]  # m²
    nombre_pieces_principales: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]


class DPEDiagnostic(BaseModel):
    """Energy performance diagnostic from ADEME"""
    n_dpe: str  # Unique identifier
    date_etablissement_dpe: datetime
    classe_consommation_energie: str  # A, B, C, D, E, F, G
    classe_estimation_ges: str  # GHG emissions class
    consommation_energie: float  # kWh EP/m²/year
    estimation_ges: float  # kg CO2/m²/year
    code_postal: str
    type_batiment: str  # "appartement", "maison"
    annee_construction: Optional[str]
    surface_habitable: float  # m²
    type_energie_principale_chauffage: str  # "électricité", "gaz", etc.
    type_installation_chauffage: Optional[str]
    type_energie_n_1: Optional[str]
    conso_chauffage: Optional[float]
    conso_ecs: Optional[float]  # Eau chaude sanitaire
    conso_refroidissement: Optional[float]
    conso_eclairage: Optional[float]
    conso_auxiliaires: Optional[float]


class GDPRConfig(BaseModel):
    """GDPR compliance configuration"""
    anonymization_level: str = "postal_code"  # "postal_code", "commune", "department"
    include_exact_addresses: bool = False
    data_retention_days: int = 90


class FrenchGovDataFetcher:
    """
    Asynchronous fetcher for French Government Open Data APIs
    with Redis caching and GDPR compliance
    """

    # API Endpoints (2026 versions)
    DVF_BASE_URL = "https://data.economie.gouv.fr/api/v2/catalog/datasets/dvf/records"
    ADEME_DPE_BASE_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe-v2-logements-existants/lines"

    # Cache TTL (seconds)
    CACHE_TTL_DVF = 86400  # 24 hours (DVF data is updated monthly)
    CACHE_TTL_DPE = 43200  # 12 hours (DPE data is updated weekly)

    # Rate limiting (requests per minute)
    RATE_LIMIT_DVF = 30
    RATE_LIMIT_DPE = 60

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF_SECONDS = [1, 3, 9]  # Exponential backoff

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        gdpr_config: Optional[GDPRConfig] = None
    ):
        """
        Initialize the data fetcher

        Args:
            redis_url: Redis connection URL
            gdpr_config: GDPR compliance configuration
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.gdpr_config = gdpr_config or GDPRConfig()
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info(f"FrenchGovDataFetcher initialized with GDPR level: {self.gdpr_config.anonymization_level}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def connect(self):
        """Establish connections to Redis and HTTP session"""
        self.redis_client = await redis.from_url(self.redis_url, decode_responses=False)
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "EcoImmoFrance/2026 (GDPR-Compliant Real Estate Platform)",
                "Accept": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        logger.info("Connections established (Redis + HTTP)")

    async def close(self):
        """Close all connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.session:
            await self.session.close()
        logger.info("Connections closed")

    def _generate_cache_key(self, prefix: str, params: Dict) -> str:
        """
        Generate a consistent cache key from parameters

        Args:
            prefix: Cache key prefix (e.g., "dvf", "dpe")
            params: Query parameters

        Returns:
            Cache key string
        """
        # Sort params for consistency
        sorted_params = sorted(params.items())
        params_str = urlencode(sorted_params)
        hash_suffix = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"ecoimmo:{prefix}:{hash_suffix}"

    async def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Retrieve data from Redis cache"""
        if not self.redis_client:
            return None

        try:
            data = await self.redis_client.get(cache_key)
            if data:
                logger.info(f"Cache HIT: {cache_key}")
                return data
            logger.debug(f"Cache MISS: {cache_key}")
            return None
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    async def _set_to_cache(self, cache_key: str, data: bytes, ttl: int):
        """Store data in Redis cache with TTL"""
        if not self.redis_client:
            return

        try:
            await self.redis_client.setex(cache_key, ttl, data)
            logger.debug(f"Cached: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    async def _fetch_with_retry(
        self,
        url: str,
        params: Dict,
        max_retries: int = MAX_RETRIES
    ) -> Optional[Dict]:
        """
        Fetch data with exponential backoff retry logic

        Args:
            url: API endpoint URL
            params: Query parameters
            max_retries: Maximum number of retry attempts

        Returns:
            JSON response or None if all retries failed
        """
        if not self.session:
            raise RuntimeError("HTTP session not initialized. Call connect() first.")

        for attempt in range(max_retries):
            try:
                async with self.session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logger.info(f"API call successful: {url}")
                    return data

            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    backoff = self.RETRY_BACKOFF_SECONDS[attempt]
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"API call failed after {max_retries} attempts: {e}")
                    return None

        return None

    def _anonymize_address(self, transaction: Dict) -> Dict:
        """
        Anonymize address data according to GDPR configuration

        Args:
            transaction: Raw transaction data

        Returns:
            Anonymized transaction data
        """
        if not self.gdpr_config.include_exact_addresses:
            # Remove exact address, keep only postal code/commune
            transaction.pop('adresse_numero', None)
            transaction.pop('adresse_nom_voie', None)

            # Optionally remove coordinates
            if self.gdpr_config.anonymization_level == "commune":
                transaction.pop('longitude', None)
                transaction.pop('latitude', None)

        return transaction

    async def fetch_dvf_transactions(
        self,
        code_postal: Optional[str] = None,
        code_commune: Optional[str] = None,
        date_min: Optional[datetime] = None,
        date_max: Optional[datetime] = None,
        type_local: Optional[str] = None,
        limit: int = 100
    ) -> List[DVFTransaction]:
        """
        Fetch property transactions from DVF database

        Args:
            code_postal: Postal code filter (e.g., "75001")
            code_commune: INSEE commune code (e.g., "75101")
            date_min: Minimum transaction date
            date_max: Maximum transaction date
            type_local: Property type ("Maison", "Appartement")
            limit: Maximum number of results

        Returns:
            List of DVF transactions
        """
        # Build query parameters
        params = {"limit": limit}
        where_clauses = []

        if code_postal:
            where_clauses.append(f"code_postal='{code_postal}'")
        if code_commune:
            where_clauses.append(f"code_commune='{code_commune}'")
        if date_min:
            where_clauses.append(f"date_mutation>='{date_min.strftime('%Y-%m-%d')}'")
        if date_max:
            where_clauses.append(f"date_mutation<='{date_max.strftime('%Y-%m-%d')}'")
        if type_local:
            where_clauses.append(f"type_local='{type_local}'")

        if where_clauses:
            params["where"] = " AND ".join(where_clauses)

        # Check cache
        cache_key = self._generate_cache_key("dvf", params)
        cached_data = await self._get_from_cache(cache_key)

        if cached_data:
            import json
            records = json.loads(cached_data)
        else:
            # Fetch from API
            response = await self._fetch_with_retry(self.DVF_BASE_URL, params)
            if not response or 'records' not in response:
                logger.error("Invalid DVF API response")
                return []

            records = response['records']

            # Cache the results
            import json
            await self._set_to_cache(
                cache_key,
                json.dumps(records).encode(),
                self.CACHE_TTL_DVF
            )

        # Parse and anonymize
        transactions = []
        for record in records[:limit]:
            fields = record.get('fields', {})

            # Apply GDPR anonymization
            fields = self._anonymize_address(fields)

            try:
                transaction = DVFTransaction(
                    id_mutation=fields.get('id_mutation', ''),
                    date_mutation=datetime.fromisoformat(fields.get('date_mutation', '').replace('Z', '+00:00')),
                    nature_mutation=fields.get('nature_mutation', ''),
                    valeur_fonciere=float(fields.get('valeur_fonciere', 0)),
                    adresse_numero=fields.get('adresse_numero'),
                    adresse_nom_voie=fields.get('adresse_nom_voie'),
                    code_postal=fields.get('code_postal', ''),
                    code_commune=fields.get('code_commune', ''),
                    nom_commune=fields.get('nom_commune', ''),
                    type_local=fields.get('type_local', ''),
                    surface_reelle_bati=fields.get('surface_reelle_bati'),
                    nombre_pieces_principales=fields.get('nombre_pieces_principales'),
                    longitude=fields.get('longitude'),
                    latitude=fields.get('latitude')
                )
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Failed to parse DVF record: {e}")
                continue

        logger.info(f"Fetched {len(transactions)} DVF transactions")
        return transactions

    async def fetch_dpe_diagnostics(
        self,
        code_postal: Optional[str] = None,
        classe_consommation: Optional[str] = None,
        type_batiment: Optional[str] = None,
        date_min: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DPEDiagnostic]:
        """
        Fetch energy performance diagnostics from ADEME

        Args:
            code_postal: Postal code filter
            classe_consommation: Energy class filter (A-G)
            type_batiment: Building type ("appartement", "maison")
            date_min: Minimum DPE establishment date
            limit: Maximum number of results

        Returns:
            List of DPE diagnostics
        """
        # Build query parameters
        params = {"size": limit}
        query_parts = []

        if code_postal:
            query_parts.append(f"Code_postal_(BAN):{code_postal}")
        if classe_consommation:
            query_parts.append(f"Classe_consommation_énergie:{classe_consommation}")
        if type_batiment:
            query_parts.append(f"Type_bâtiment:{type_batiment}")
        if date_min:
            query_parts.append(f"Date_établissement_DPE:>={date_min.strftime('%Y-%m-%d')}")

        if query_parts:
            params["q"] = " AND ".join(query_parts)

        # Check cache
        cache_key = self._generate_cache_key("dpe", params)
        cached_data = await self._get_from_cache(cache_key)

        if cached_data:
            import json
            results = json.loads(cached_data)
        else:
            # Fetch from API
            response = await self._fetch_with_retry(self.ADEME_DPE_BASE_URL, params)
            if not response or 'results' not in response:
                logger.error("Invalid ADEME DPE API response")
                return []

            results = response['results']

            # Cache the results
            import json
            await self._set_to_cache(
                cache_key,
                json.dumps(results).encode(),
                self.CACHE_TTL_DPE
            )

        # Parse diagnostics
        diagnostics = []
        for result in results[:limit]:
            try:
                diagnostic = DPEDiagnostic(
                    n_dpe=result.get('N°DPE', ''),
                    date_etablissement_dpe=datetime.fromisoformat(result.get('Date_établissement_DPE', '').replace('Z', '+00:00')),
                    classe_consommation_energie=result.get('Classe_consommation_énergie', ''),
                    classe_estimation_ges=result.get('Classe_estimation_GES', ''),
                    consommation_energie=float(result.get('Consommation_énergie', 0)),
                    estimation_ges=float(result.get('Estimation_GES', 0)),
                    code_postal=result.get('Code_postal_(BAN)', ''),
                    type_batiment=result.get('Type_bâtiment', ''),
                    annee_construction=result.get('Année_construction'),
                    surface_habitable=float(result.get('Surface_habitable_logement', 0)),
                    type_energie_principale_chauffage=result.get('Type_énergie_principale_chauffage', ''),
                    type_installation_chauffage=result.get('Type_installation_chauffage'),
                    type_energie_n_1=result.get('Type_énergie_n°1'),
                    conso_chauffage=result.get('Conso_chauffage_é_finale'),
                    conso_ecs=result.get('Conso_ECS_é_finale'),
                    conso_refroidissement=result.get('Conso_refroidissement_é_finale'),
                    conso_eclairage=result.get('Conso_éclairage_é_finale'),
                    conso_auxiliaires=result.get('Conso_auxiliaires_é_finale')
                )
                diagnostics.append(diagnostic)
            except Exception as e:
                logger.warning(f"Failed to parse DPE record: {e}")
                continue

        logger.info(f"Fetched {len(diagnostics)} DPE diagnostics")
        return diagnostics

    async def cross_reference_dvf_dpe(
        self,
        code_postal: str,
        date_range_days: int = 365
    ) -> List[Dict[str, Any]]:
        """
        Cross-reference DVF transactions with DPE diagnostics
        This is a core feature for EcoImmo France 2026

        Args:
            code_postal: Postal code to analyze
            date_range_days: Date range for transactions (default: 1 year)

        Returns:
            List of enriched property data (DVF + DPE)
        """
        date_min = datetime.now() - timedelta(days=date_range_days)

        # Fetch both datasets in parallel
        dvf_task = self.fetch_dvf_transactions(
            code_postal=code_postal,
            date_min=date_min,
            limit=200
        )
        dpe_task = self.fetch_dpe_diagnostics(
            code_postal=code_postal,
            date_min=date_min,
            limit=200
        )

        transactions, diagnostics = await asyncio.gather(dvf_task, dpe_task)

        # Create DPE lookup by postal code + approximate surface
        dpe_map = {}
        for dpe in diagnostics:
            key = f"{dpe.code_postal}_{int(dpe.surface_habitable / 10) * 10}"  # Round to nearest 10m²
            if key not in dpe_map:
                dpe_map[key] = []
            dpe_map[key].append(dpe)

        # Enrich transactions with DPE data
        enriched = []
        for txn in transactions:
            if not txn.surface_reelle_bati:
                continue

            # Try to find matching DPE
            surface_key = f"{txn.code_postal}_{int(txn.surface_reelle_bati / 10) * 10}"
            matching_dpes = dpe_map.get(surface_key, [])

            if matching_dpes:
                # Take the most recent DPE
                most_recent_dpe = max(matching_dpes, key=lambda d: d.date_etablissement_dpe)

                enriched.append({
                    'transaction': txn.dict(),
                    'dpe': most_recent_dpe.dict(),
                    'confidence': 'medium'  # Surface-based matching
                })
            else:
                # No DPE found
                enriched.append({
                    'transaction': txn.dict(),
                    'dpe': None,
                    'confidence': 'none'
                })

        logger.info(f"Cross-referenced {len(enriched)} properties ({len([e for e in enriched if e['dpe']])} with DPE)")
        return enriched


# Example usage
if __name__ == "__main__":
    async def main():
        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Example: Fetch data for Paris 15th arrondissement
        async with FrenchGovDataFetcher() as fetcher:
            # Fetch recent transactions
            transactions = await fetcher.fetch_dvf_transactions(
                code_postal="75015",
                date_min=datetime(2025, 1, 1),
                type_local="Appartement",
                limit=10
            )

            print(f"\nFound {len(transactions)} transactions in 75015")
            for txn in transactions[:3]:
                print(f"  - {txn.type_local} {txn.surface_reelle_bati}m² @ {txn.valeur_fonciere:,.0f} EUR")

            # Fetch DPE diagnostics
            diagnostics = await fetcher.fetch_dpe_diagnostics(
                code_postal="75015",
                limite=10
            )

            print(f"\nFound {len(diagnostics)} DPE diagnostics in 75015")
            for dpe in diagnostics[:3]:
                print(f"  - {dpe.type_batiment} {dpe.surface_habitable}m² - Classe {dpe.classe_consommation_energie}")

            # Cross-reference
            enriched = await fetcher.cross_reference_dvf_dpe("75015", date_range_days=180)
            print(f"\nCross-referenced {len(enriched)} properties")
            matches = [e for e in enriched if e['dpe']]
            print(f"  - {len(matches)} with DPE data ({len(matches)/len(enriched)*100:.1f}%)")

    asyncio.run(main())
