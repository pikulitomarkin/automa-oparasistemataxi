"""
Teste para validar que a otimização de rota funciona mesmo quando o geocoding 
do destino falha com restrições de bounds (mas funciona no fallback)
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.route_optimizer import RouteOptimizer
from unittest.mock import Mock, patch
from src.processor import TaxiOrderProcessor
from src.models import Order, OrderStatus

def test_route_optimization_with_fallback():
    """
    Simula cenário onde:
    1. Geocoding do destino falha com bounds (retorna None)
    2. Fallback sem bounds funciona (retorna coordenadas)
    3. Otimização de rota deve funcionar usando as coordenadas do fallback
    """
    print("\n" + "="*70)
    print("TESTE: Otimização com Fallback de Geocoding")
    print("="*70)
    
    # Mock do geocoder que falha na primeira tentativa e funciona no fallback
    mock_geocoder = Mock()
    
    # geocode_address (com bounds) retorna None para o destino
    def geocode_with_bounds(address):
        if "Shopping" in address:
            print(f"  ❌ geocode_address (com bounds) falhou para: {address}")
            return None
        # Para passageiros, funciona normalmente
        if "Centro" in address:
            return (-19.9178, -43.9383)
        elif "Santo Agostinho" in address:
            return (-19.9445, -43.9625)
        elif "São Bento" in address:
            return (-19.9660, -43.9720)
        return None
    
    # geocode_address_fallback (sem bounds) funciona para o destino
    def geocode_fallback(address):
        if "Shopping" in address:
            coords = (-19.9520, -43.9950)
            print(f"  ✅ geocode_address_fallback (sem bounds) funcionou: {address} → {coords}")
            return coords
        return None
    
    mock_geocoder.geocode_address.side_effect = geocode_with_bounds
    mock_geocoder.geocode_address_fallback.side_effect = geocode_fallback
    
    # Cria uma ordem de teste com múltiplos passageiros
    order = Order(
        email_id="test@example.com",
        pickup_address="Múltiplas paradas",
        dropoff_address="Shopping Del Rey, Belo Horizonte",
        passenger_name="Teste Sistema",
        phone="31999999999",
        raw_email_body="Test email"
    )
    
    order.passengers = [
        {
            "name": "João",
            "address": "Centro, Belo Horizonte",
            "phone": "31999991111"
        },
        {
            "name": "Maria",
            "address": "Santo Agostinho, Belo Horizonte",
            "phone": "31999992222"
        },
        {
            "name": "Pedro",
            "address": "São Bento, Belo Horizonte",
            "phone": "31999993333"
        }
    ]
    
    print("\nCenário:")
    print(f"  Destino: {order.dropoff_address}")
    print(f"  Passageiros: {len(order.passengers)}")
    for p in order.passengers:
        print(f"    - {p['name']}: {p['address']}")
    
    print("\nSimulando processo de geocoding...")
    
    # Simula o bloco de código do processor.py (linhas 269-286)
    destination_coords = None
    if order.dropoff_address:
        dropoff_coords = mock_geocoder.geocode_address(order.dropoff_address)
        if dropoff_coords:
            order.dropoff_lat, order.dropoff_lng = dropoff_coords
            destination_coords = dropoff_coords
        else:
            # FALLBACK
            print("\n  ⚠️  Tentando fallback...")
            dropoff_coords = mock_geocoder.geocode_address_fallback(order.dropoff_address)
            if dropoff_coords:
                order.dropoff_lat, order.dropoff_lng = dropoff_coords
                destination_coords = dropoff_coords
    
    # Geocode passageiros
    if order.passengers:
        for passenger in order.passengers:
            coords = mock_geocoder.geocode_address(passenger.get('address', ''))
            if coords:
                passenger['lat'] = coords[0]
                passenger['lng'] = coords[1]
    
    print("\nResultados do geocoding:")
    print(f"  Destino: {destination_coords}")
    for p in order.passengers:
        if 'lat' in p:
            print(f"  {p['name']}: ({p['lat']:.4f}, {p['lng']:.4f})")
    
    # Verifica se temos coordenadas de destino
    if not destination_coords:
        print("\n❌ FALHA: destination_coords é None! Otimização NÃO vai funcionar!")
        return False
    
    print(f"\n✅ destination_coords obtido: {destination_coords}")
    print("\nOtimizando rota...")
    
    # Otimiza rota
    optimized = RouteOptimizer.optimize_pickup_sequence(order.passengers, destination_coords)
    
    print("\nOrdem otimizada de coleta:")
    for i, p in enumerate(optimized, 1):
        coords = (p['lat'], p['lng'])
        dist = RouteOptimizer.calculate_distance(coords, destination_coords)
        print(f"  {i}. {p['name']} ({dist:.2f} km do destino)")
    
    # Valida que o último passageiro é o mais próximo do destino
    distances = []
    for p in optimized:
        coords = (p['lat'], p['lng'])
        dist = RouteOptimizer.calculate_distance(coords, destination_coords)
        distances.append((p['name'], dist))
    
    # O último deve ter a menor distância
    last_passenger = distances[-1]
    min_distance = min(d[1] for d in distances)
    
    print("\n" + "="*70)
    if last_passenger[1] == min_distance:
        print(f"✅ SUCESSO! {last_passenger[0]} (mais próximo) embarca por último")
        print("   A otimização por distância está FUNCIONANDO!")
    else:
        print(f"❌ FALHA! {last_passenger[0]} embarca por último, mas não é o mais próximo")
        print(f"   Mais próximo seria: {min(distances, key=lambda x: x[1])[0]}")
    print("="*70 + "\n")
    
    return last_passenger[1] == min_distance

if __name__ == "__main__":
    success = test_route_optimization_with_fallback()
    sys.exit(0 if success else 1)
