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
        
        # Normaliza o endereço
        normalized_address = self._normalize_address(address)
        
        for attempt in range(max_retries):
            try:
                location = self.geolocator.geocode(normalized_address)
                
                if location:
                    lat, lng = location.latitude, location.longitude
                    logger.info(
                        f"Geocoded '{address}' -> ({lat:.6f}, {lng:.6f})"
                    )
                    return (lat, lng)
                else:
                    logger.warning(f"No results found for address: {address}")
                    return None
                    
            except GeocoderTimedOut:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Geocoding timeout for '{address}', "
                        f"retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Geocoding failed after {max_retries} attempts: {address}")
                    return None
                    
            except GeocoderServiceError as e:
                logger.error(f"Geocoding service error for '{address}': {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error in geocoding '{address}': {e}")
                return None
        
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
        # Remove espaços extras
        normalized = " ".join(address.split())
        
        # Se não menciona cidade, adiciona Belo Horizonte, MG (padrão para táxis locais)
        if "belo horizonte" not in normalized.lower() and "BH" not in normalized.upper():
            # Verifica se já tem alguma cidade mencionada
            if not any(city in normalized.lower() for city in ["minas gerais", "mg", ","]):
                normalized += ", Belo Horizonte, MG, Brasil"
        
        return normalized
    
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
