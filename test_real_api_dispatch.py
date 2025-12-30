#!/usr/bin/env python3
"""
Teste REAL da API MinasTaxi com pedido completo.
Usa o cliente configurado com adapter SSL.
"""
import os
from dotenv import load_dotenv
from src.services.minastaxi_client import MinasTaxiClient
from src.models.order import Order, OrderStatus
from datetime import datetime, timezone

# Carrega .env
load_dotenv()

def test_real_dispatch():
    """Testa dispatch real usando o cliente configurado."""
    print("🚀 TESTE REAL - DISPATCH MINASTAXI API")
    print("=" * 50)
    
    try:
        # Cria cliente
        client = MinasTaxiClient(
            api_url=os.getenv('MINASTAXI_API_URL'),
            user_id=os.getenv('MINASTAXI_USER_ID'),
            password=os.getenv('MINASTAXI_PASSWORD'),
            auth_header=os.getenv('MINASTAXI_AUTH_HEADER')
        )
        
        print("✅ Cliente criado")
        
        # Teste de conectividade primeiro
        print("🔍 Testando conectividade...")
        if not client.test_connection():
            print("❌ Falha na conectividade")
            return False
        
        print("✅ Conectividade OK")
        
        # Cria order de teste
        order = Order(
            email_id="test_real_api_dispatch",
            passenger_name="Ana Silva Rodrigues, Carlos Eduardo Santos, Maria Fernanda Costa, João Paulo Oliveira",
            phone="31999999926",
            pickup_address="Rua Rio de Janeiro, 500, Centro, Belo Horizonte, MG",
            pickup_lat=-19.918101,
            pickup_lng=-43.938340,
            dropoff_address="Rua Curitiba, 832, Centro, Belo Horizonte, MG", 
            dropoff_lat=-19.914033,
            dropoff_lng=-43.940021,
            pickup_time=datetime(2025, 12, 30, 14, 0, tzinfo=timezone.utc),
            raw_email_body="TESTE API REAL - 4 passageiros",
            status=OrderStatus.GEOCODED
        )
        
        # Adiciona passageiros individuais
        order.passengers = [
            {
                "name": "Ana Silva Rodrigues",
                "phone": "31999999926", 
                "address": "Rua Rio de Janeiro, 500, Centro, Belo Horizonte, MG",
                "lat": -19.918101,
                "lng": -43.938340
            },
            {
                "name": "Carlos Eduardo Santos",
                "phone": "31999999926",
                "address": "Avenida Afonso Pena, 1200, Centro, Belo Horizonte, MG", 
                "lat": -19.921375,
                "lng": -43.937091
            },
            {
                "name": "Maria Fernanda Costa",
                "phone": "31999999926",
                "address": "Rua da Bahia, 800, Centro, Belo Horizonte, MG",
                "lat": -19.918631,
                "lng": -43.935743
            },
            {
                "name": "João Paulo Oliveira",
                "phone": "31999999926",
                "address": "Praça da Liberdade, 1, Funcionários, Belo Horizonte, MG",
                "lat": -19.932310,  # Coordenadas corrigidas
                "lng": -43.936490
            }
        ]
        
        print(f"📋 Order criada: {len(order.passengers)} passageiros")
        print(f"📅 Pickup time: {order.pickup_time}")
        print(f"📍 Origem: {order.pickup_address}")
        print(f"🎯 Destino: {order.dropoff_address}")
        
        # DESPACHA PARA API REAL
        print("\n🚀 DESPACHANDO PARA API REAL...")
        print("-" * 30)
        
        response = client.dispatch_order(order)
        
        print(f"\n✅ RESPOSTA DA API:")
        print(f"🎯 Sucesso: {response.get('success')}")
        print(f"🆔 Order ID: {response.get('order_id')}")
        print(f"🆔 Ride ID: {response.get('ride_id')}")
        print(f"📊 Status: {response.get('status')}")
        print(f"💬 Mensagem: {response.get('message')}")
        
        if response.get('success'):
            print("\n🎉 DISPATCH REALIZADO COM SUCESSO!")
            print("🚕 Pedido enviado para MinasTaxi API")
            print("🔍 Verificar no painel MinasTaxi se apareceu")
            return True
        else:
            print("\n❌ DISPATCH FALHOU")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_dispatch()
    if success:
        print("\n🎯 RESULTADO: API FUNCIONOU!")
    else:
        print("\n⚠️ RESULTADO: API COM PROBLEMAS")