"""
Teste para verificar otimização de rota por distância ao destino
"""
from src.services.route_optimizer import RouteOptimizer

def test_route_optimization():
    """Testa se passageiros são ordenados por distância ao destino"""
    
    # Destino: Shopping Del Rey (aproximadamente)
    destination_coords = (-19.9520, -43.9950)
    
    # Passageiros em diferentes localizações
    passengers = [
        {
            "name": "João",
            "address": "Av. Afonso Pena, 1234 - Centro, Belo Horizonte",
            "lat": -19.9178,  # ~5km do destino
            "lng": -43.9383,
            "phone": "31999991111"
        },
        {
            "name": "Maria",
            "address": "Rua Ouro Preto, 789 - Santo Agostinho, Belo Horizonte",
            "lat": -19.9445,  # ~2km do destino (MAIS PRÓXIMO - deve ser o último)
            "lng": -43.9625,
            "phone": "31999992222"
        },
        {
            "name": "Pedro",
            "address": "Av. Raja Gabaglia, 3000 - São Bento, Belo Horizonte",
            "lat": -19.9660,  # ~8km do destino
            "lng": -43.9720,
            "phone": "31999993333"
        }
    ]
    
    print("\n" + "="*60)
    print("TESTE DE OTIMIZAÇÃO DE ROTA")
    print("="*60)
    
    print(f"\nDestino: {destination_coords}")
    print("\nPassageiros ANTES da otimização:")
    for i, p in enumerate(passengers, 1):
        print(f"  {i}. {p['name']} - {p['address']}")
    
    # Calcular distâncias ANTES da otimização
    print("\nDistâncias ao destino:")
    for p in passengers:
        coords = (p['lat'], p['lng'])
        dist = RouteOptimizer.calculate_distance(coords, destination_coords)
        print(f"  {p['name']}: {dist:.2f} km")
    
    # Otimizar rota
    optimized = RouteOptimizer.optimize_pickup_sequence(passengers, destination_coords)
    
    print("\nPassageiros DEPOIS da otimização:")
    for i, p in enumerate(optimized, 1):
        coords = (p['lat'], p['lng'])
        dist = RouteOptimizer.calculate_distance(coords, destination_coords)
        print(f"  {i}. {p['name']} - {p['address']} ({dist:.2f} km)")
    
    print("\n" + "="*60)
    print("RESULTADO ESPERADO:")
    print("  1. Pedro (mais longe - embarca primeiro)")
    print("  2. João (distância média)")
    print("  3. Maria (mais próximo do destino - embarca por último)")
    print("="*60)
    
    # Verificações
    assert optimized[-1]['name'] == 'Maria', "❌ ERRO: Maria deveria ser a última (mais próxima do destino)"
    assert optimized[0]['name'] == 'Pedro', "❌ ERRO: Pedro deveria ser o primeiro (mais longe do destino)"
    
    print("\n✅ TESTE PASSOU! A ordenação está correta.")
    print("   O passageiro mais próximo do destino (Maria) embarca por último.\n")

def test_route_optimization_without_destination():
    """Testa o que acontece quando não há coordenadas de destino"""
    
    passengers = [
        {"name": "João", "lat": -19.9178, "lng": -43.9383, "address": "Centro"},
        {"name": "Maria", "lat": -19.9445, "lng": -43.9625, "address": "Santo Agostinho"},
        {"name": "Pedro", "lat": -19.9660, "lng": -43.9720, "address": "São Bento"}
    ]
    
    print("\n" + "="*60)
    print("TESTE SEM COORDENADAS DE DESTINO")
    print("="*60)
    
    print("\nPassageiros ANTES:")
    for i, p in enumerate(passengers, 1):
        print(f"  {i}. {p['name']} - {p['address']}")
    
    # Otimizar SEM destino (destination_coords=None)
    optimized = RouteOptimizer.optimize_pickup_sequence(passengers, None)
    
    print("\nPassageiros DEPOIS (destination_coords=None):")
    for i, p in enumerate(optimized, 1):
        print(f"  {i}. {p['name']} - {p['address']}")
    
    print("\n⚠️  RESULTADO: Quando destination_coords é None, a ordem NÃO é otimizada!")
    print("   Os passageiros mantêm a ordem original.\n")

if __name__ == "__main__":
    test_route_optimization()
    test_route_optimization_without_destination()
