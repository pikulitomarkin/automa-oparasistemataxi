"""
Script de Teste: Dispatch DIRETO para MinasTaxi API
Pula LLM e usa dados já extraídos para testar apenas a API MinasTaxi
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.minastaxi_client import MinasTaxiClient
from src.models.order import Order, OrderStatus

# Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), '.env')
for key in ['MINASTAXI_API_URL', 'MINASTAXI_USER_ID', 'MINASTAXI_PASSWORD', 'MINASTAXI_AUTH_HEADER']:
    if key in os.environ:
        del os.environ[key]
load_dotenv(env_path, override=True)


def test_direct_dispatch():
    """Testa dispatch direto para MinasTaxi com dados simulados"""
    
    print("=" * 80)
    print("🚕 TESTE DIRETO - DISPATCH PARA MINASTAXI API")
    print("=" * 80)
    print()
    
    # ============================================================================
    # 1. DADOS SIMULADOS (como se viessem do LLM)
    # ============================================================================
    print("📊 DADOS DO PEDIDO (simulados):")
    print()
    
    order = Order(
        email_id="test_direct_dispatch",
        passenger_name="Harlle Jonathan da Rocha",
        phone="37998742019",
        pickup_address="CSN Mineração, Congonhas, MG",
        dropoff_address="Belo Horizonte, MG",
        pickup_time=datetime(2025, 9, 6, 15, 30, 0),
        pickup_lat=-20.4872495,
        pickup_lng=-43.8950818,
        dropoff_lat=-19.9227318,
        dropoff_lng=-43.9450948,
        raw_email_body="CC:20063",
        status=OrderStatus.GEOCODED
    )
    
    print(f"   👤 Nome: {order.passenger_name}")
    print(f"   📱 Telefone: {order.phone}")
    print(f"   📍 Origem: {order.pickup_address}")
    print(f"      Coordenadas: ({order.pickup_lat}, {order.pickup_lng})")
    print(f"   🎯 Destino: {order.dropoff_address}")
    print(f"      Coordenadas: ({order.dropoff_lat}, {order.dropoff_lng})")
    print(f"   🕐 Horário: {order.pickup_time}")
    print(f"   📝 Notas: {order.raw_email_body}")
    print()
    
    # ============================================================================
    # 2. VERIFICAR CREDENCIAIS
    # ============================================================================
    api_url = os.getenv("MINASTAXI_API_URL")
    user_id = os.getenv("MINASTAXI_USER_ID")
    password = os.getenv("MINASTAXI_PASSWORD")
    auth_header = os.getenv("MINASTAXI_AUTH_HEADER")
    
    print("=" * 80)
    print("🔑 CREDENCIAIS MINASTAXI")
    print("=" * 80)
    print(f"   API URL: {api_url}")
    print(f"   User ID: {user_id}")
    print(f"   Password: {'*' * len(password) if password else 'None'}")
    print(f"   Auth Header: {auth_header[:30]}..." if auth_header else "None")
    print()
    
    if not all([api_url, user_id, password, auth_header]):
        print("❌ ERRO: Credenciais não configuradas!")
        return
    
    # ============================================================================
    # 3. INICIALIZAR CLIENT
    # ============================================================================
    print("=" * 80)
    print("🚀 INICIALIZANDO CLIENTE MINASTAXI")
    print("=" * 80)
    
    minastaxi_client = MinasTaxiClient(
        api_url=api_url,
        user_id=user_id,
        password=password,
        auth_header=auth_header
    )
    
    print("✅ Cliente inicializado")
    print()
    
    # ============================================================================
    # 4. PAYLOAD
    # ============================================================================
    print("=" * 80)
    print("📦 PAYLOAD QUE SERÁ ENVIADO")
    print("=" * 80)
    
    import json
    from datetime import timezone
    
    # Converte datetime para UNIX timestamp
    pickup_timestamp = int(order.pickup_time.replace(tzinfo=timezone.utc).timestamp())
    
    payload = {
        "partner": "1",
        "user": user_id,
        "password": password,
        "request_id": f"test_{order.email_id}",
        "date_ride": pickup_timestamp,
        "users": [{
            "name": order.passenger_name,
            "phone": order.phone
        }],
        "destinations": [{
            "address": order.dropoff_address,
            "lat": order.dropoff_lat,
            "lng": order.dropoff_lng
        }],
        "origin": {
            "address": order.pickup_address,
            "lat": order.pickup_lat,
            "lng": order.pickup_lng
        }
    }
    
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    # ============================================================================
    # 5. CONFIRMAÇÃO
    # ============================================================================
    print("=" * 80)
    print("⚠️  ATENÇÃO")
    print("=" * 80)
    print("Isso enviará um pedido REAL para a API MinasTaxi!")
    print(f"Endpoint: {api_url}/rideCreate")
    print()
    confirmation = input("🤔 Deseja realmente enviar? (digite 'SIM' para confirmar): ")
    
    if confirmation.upper() != "SIM":
        print("\n❌ Cancelado pelo usuário.")
        return
    
    # ============================================================================
    # 6. DISPATCH
    # ============================================================================
    print()
    print("=" * 80)
    print("📤 ENVIANDO PARA MINASTAXI...")
    print("=" * 80)
    
    try:
        result = minastaxi_client.dispatch_order(order)
        
        print()
        print("=" * 80)
        if result and result.get('success'):
            print("✅ SUCESSO - PEDIDO DESPACHADO!")
            print("=" * 80)
            print(f"   🎉 Ride ID: {result.get('ride_id')}")
            print(f"   📋 Status: DISPATCHED")
            
            if result.get('response'):
                print(f"\n   📨 Resposta completa da API:")
                print(json.dumps(result['response'], indent=2, ensure_ascii=False))
        else:
            print("❌ FALHA NO DISPATCH")
            print("=" * 80)
            print(f"   ❌ Erro: {result.get('error', 'Erro desconhecido')}")
            
            if result.get('response'):
                print(f"\n   📨 Resposta da API:")
                print(json.dumps(result['response'], indent=2, ensure_ascii=False))
    
    except Exception as e:
        print()
        print("=" * 80)
        print("💥 ERRO DURANTE DISPATCH")
        print("=" * 80)
        print(f"   Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    test_direct_dispatch()
