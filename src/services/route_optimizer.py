"""
Otimizador de rota para múltiplos passageiros
"""
import math
from typing import List, Dict, Tuple, Optional, Any

try:
    from geopy.distance import geodesic
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

class RouteOptimizer:
    """Otimiza ordem de coleta dos passageiros"""
    
    @staticmethod
    def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calcula distância entre duas coordenadas em km"""
        try:
            if HAS_GEOPY:
                return geodesic(coord1, coord2).kilometers
            else:
                # Fallback: distância euclidiana simples
                lat1, lng1 = coord1
                lat2, lng2 = coord2
                return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111  # ~111km por grau
        except:
            # Fallback: distância euclidiana simples
            lat1, lng1 = coord1
            lat2, lng2 = coord2
            return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111  # ~111km por grau
    
    @staticmethod
    def optimize_pickup_sequence(
        passengers: List[Dict[str, Any]], 
        destination_coords: Optional[Tuple[float, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Otimiza sequência de coleta dos passageiros.
        Último passageiro deve ser mais próximo do destino.
        
        Args:
            passengers: Lista de passageiros com lat/lng
            destination_coords: Coordenadas do destino final
            
        Returns:
            Lista otimizada de passageiros
        """
        if len(passengers) <= 1:
            return passengers
        
        # Se temos coordenadas do destino, otimiza por proximidade
        if destination_coords:
            # Calcula distância de cada passageiro ao destino
            for passenger in passengers:
                if 'lat' in passenger and 'lng' in passenger:
                    passenger_coords = (passenger['lat'], passenger['lng'])
                    distance = RouteOptimizer.calculate_distance(passenger_coords, destination_coords)
                    passenger['_distance_to_destination'] = distance
                else:
                    passenger['_distance_to_destination'] = float('inf')
            
            # Ordena: primeiro os mais longe, último o mais próximo do destino
            optimized = sorted(passengers, key=lambda p: p.get('_distance_to_destination', float('inf')), reverse=True)
            
            # Remove campo temporário
            for passenger in optimized:
                passenger.pop('_distance_to_destination', None)
            
            return optimized
        
        # Se não temos destino, mantém ordem original
        return passengers
    
    @staticmethod
    def generate_route_summary(passengers: List[Dict[str, Any]]) -> str:
        """Gera resumo da rota otimizada"""
        if len(passengers) <= 1:
            return passengers[0]['address'] if passengers else "Sem passageiros"
        
        addresses = [f"{i+1}. {p['address']}" for i, p in enumerate(passengers)]
        return f"Rota otimizada:\n" + "\n".join(addresses)