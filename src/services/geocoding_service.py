"""
Geocoding service for address to coordinates conversion.
"""
import logging
from typing import Optional, Tuple
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Serviço de geocodificação de endereços.
    Suporta Nominatim (gratuito) e Google Maps API.
    """
    
    def __init__(
        self,
        use_google: bool = False,
        google_api_key: Optional[str] = None,
        timeout: int = 10
    ):
        """
        Inicializa o serviço de geocoding.
        
        Args:
            use_google: Se True, usa Google Maps API (requer chave).
            google_api_key: Chave da API do Google Maps.
            timeout: Timeout para requisições em segundos.
        """
        self.timeout = timeout
        self.use_google = use_google
        
        if use_google and google_api_key:
            self.geolocator = GoogleV3(api_key=google_api_key, timeout=timeout)
            logger.info("Geocoding service initialized with Google Maps API")
        else:
            # Nominatim é gratuito mas tem rate limits
            self.geolocator = Nominatim(
                user_agent="taxi_automation_system",
                timeout=timeout
            )
            logger.info("Geocoding service initialized with Nominatim (OpenStreetMap)")
    
    def geocode_address(
        self,
        address: str,
        max_retries: int = 3
    ) -> Optional[Tuple[float, float]]:
        """
        Converte um endereço em coordenadas (latitude, longitude).
        
        Args:
            address: Endereço completo em texto.
            max_retries: Número máximo de tentativas em caso de timeout.
            
        Returns:
            Tupla (latitude, longitude) ou None se falhar.
        """
        if not address or address.strip() == "":
            logger.warning("Empty address provided for geocoding")
            return None
        
        # Normaliza o endereço e gera variantes para fallback
        normalized_address = self._normalize_address(address)
        variants = [normalized_address]
        variants += self._generate_address_variants(normalized_address)

        for idx, candidate in enumerate(variants):
            for attempt in range(max_retries):
                try:
                    location = self.geolocator.geocode(candidate)

                    if location:
                        lat, lng = location.latitude, location.longitude
                        logger.info(f"Geocoded '{address}' using '{candidate}' -> ({lat:.6f}, {lng:.6f})")
                        return (lat, lng)
                    else:
                        logger.debug(f"No results for candidate: '{candidate}'")
                        break  # tenta próxima variante

                except GeocoderTimedOut:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(
                            f"Geocoding timeout for '{candidate}', retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Geocoding failed after {max_retries} attempts for candidate: {candidate}")
                        break

                except GeocoderServiceError as e:
                    logger.error(f"Geocoding service error for '{candidate}': {e}")
                    break

                except Exception as e:
                    logger.error(f"Unexpected error in geocoding '{candidate}': {e}")
                    break

            # small delay between variant attempts for Nominatim
            if not self.use_google:
                time.sleep(0.5)

        logger.warning(f"No results found for address after trying variants: {address}")
        return None
    
    def geocode_batch(
        self,
        addresses: list[str],
        delay: float = 1.0
    ) -> dict[str, Optional[Tuple[float, float]]]:
        """
        Geocodifica múltiplos endereços em batch.
        
        Args:
            addresses: Lista de endereços.
            delay: Delay entre requisições em segundos (para respeitar rate limits).
            
        Returns:
            Dicionário mapeando endereços para coordenadas.
        """
        results = {}
        
        for i, address in enumerate(addresses):
            results[address] = self.geocode_address(address)
            
            # Delay entre requisições (importante para Nominatim)
            if i < len(addresses) - 1 and not self.use_google:
                time.sleep(delay)
        
        success_count = sum(1 for v in results.values() if v is not None)
        logger.info(
            f"Batch geocoding completed: {success_count}/{len(addresses)} successful"
        )
        
        return results
    
    def reverse_geocode(
        self,
        lat: float,
        lng: float
    ) -> Optional[str]:
        """
        Converte coordenadas em endereço (reverse geocoding).
        
        Args:
            lat: Latitude.
            lng: Longitude.
            
        Returns:
            Endereço em texto ou None se falhar.
        """
        try:
            location = self.geolocator.reverse((lat, lng), exactly_one=True)
            
            if location:
                address = location.address
                logger.info(f"Reverse geocoded ({lat}, {lng}) -> '{address}'")
                return address
            else:
                logger.warning(f"No address found for coordinates ({lat}, {lng})")
                return None
                
        except Exception as e:
            logger.error(f"Error in reverse geocoding ({lat}, {lng}): {e}")
            return None
    
    def _normalize_address(self, address: str) -> str:
        """
        Normaliza o endereço para melhorar precisão do geocoding.
        
        Args:
            address: Endereço original.
            
        Returns:
            Endereço normalizado.
        """
        # Remove espaços extras e caracteres de traço/en-dash squish
        s = address.replace('\u2013', '-').replace('\u2014', '-')
        s = s.replace('\u00A0', ' ')
        normalized = " ".join(s.split())

        # Remove tokens comuns que atrapalham geocoding (Número:, N°, BAIRRO etc.)
        normalized = normalized.replace('Número:', 'Nº').replace('Número', 'Nº')
        normalized = normalized.replace('BAIRRO', 'Bairro')

        # Remove excessos de símbolos e parênteses longos
        normalized = re.sub(r"\s*\([^\)]{50,}\)", "", normalized)

        # Substitui múltiplas vírgulas por uma
        normalized = re.sub(r",{2,}", ",", normalized)

        # Se há ' - ' com quebras estranhas, normaliza para vírgula
        normalized = normalized.replace(' - ', ', ')

        # Expansões simples para empresas/locais conhecidos
        known_mappings = {
            'Delp Engenharia Vespasiano': 'Av. das Nações, 999, Distrito Industrial, Vespasiano, MG, Brasil',
            'Delp Engenharia': 'Av. das Nações, 999, Distrito Industrial, Vespasiano, MG, Brasil',
            'Aeroporto Confins': 'Aeroporto Internacional Tancredo Neves - Confins, MG'
        }
        for k, v in known_mappings.items():
            if k.lower() in normalized.lower():
                return v

        # Se não menciona estado/cidade, adiciona Belo Horizonte, MG (padrão local)
        lower = normalized.lower()
        if not any(x in lower for x in ['mg', 'minas gerais', 'belo horizonte', 'belo-horizonte', 'vespasiano', 'contagem']):
            normalized += ', Belo Horizonte, MG, Brasil'

        return normalized

    def _generate_address_variants(self, normalized: str) -> list:
        """
        Gera variantes mais simples do endereço para aumentar chances de geocoding.
        Estratégias:
        - Remover conteúdo entre parênteses
        - Manter somente logradouro + número + cidade
        - Remover termos como 'Bairro' e 'Nº'
        - Tentar versão curta com apenas logradouro + cidade
        """
        variants = []

        # Strip parentheses content
        no_paren = re.sub(r"\([^\)]*\)", '', normalized).strip()
        if no_paren != normalized:
            variants.append(no_paren)

        # Remove tokens como 'Bairro', 'Nº', 'Número'
        simple = re.sub(r'(?i)\b(Bairro|Bairro:|Nº|Nº:|Número|Número:)\b', '', no_paren)
        simple = re.sub(r'\s{2,}', ' ', simple).strip()
        if simple and simple not in variants:
            variants.append(simple)

        # Try just street + city (split by comma)
        parts = [p.strip() for p in simple.split(',') if p.strip()]
        if len(parts) >= 2:
            short = ', '.join(parts[:2])
            if 'brasil' not in short.lower():
                short += ', Brasil'
            variants.append(short)

        # Last-resort: keep only last two parts (often city and state)
        if len(parts) >= 2:
            tail = ', '.join(parts[-2:])
            variants.append(tail)

        return variants
    
    def calculate_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """
        Calcula a distância entre dois pontos usando Haversine.
        
        Args:
            lat1, lng1: Coordenadas do primeiro ponto.
            lat2, lng2: Coordenadas do segundo ponto.
            
        Returns:
            Distância em quilômetros.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Raio da Terra em km
        R = 6371.0
        
        # Converte para radianos
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)
        
        # Diferenças
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Fórmula de Haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
