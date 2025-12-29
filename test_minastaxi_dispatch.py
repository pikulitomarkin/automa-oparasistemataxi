"""
Script de Teste: Dispatch Completo para MinasTaxi API
Simula o fluxo completo: Email → LLM → Geocoding → MinasTaxi
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.llm_extractor import LLMExtractor
from src.services.email_reader import EmailMessage
from src.services.geocoding_service import GeocodingService
from src.services.minastaxi_client import MinasTaxiClient
from src.models.order import Order, OrderStatus

# Carrega variáveis de ambiente do arquivo .env no diretório atual
# Limpa variáveis antigas primeiro
for key in ['MINASTAXI_API_URL', 'MINASTAXI_USER_ID', 'MINASTAXI_PASSWORD', 'MINASTAXI_AUTH_HEADER']:
    if key in os.environ:
        del os.environ[key]

env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"📁 Carregando: {env_path}")
print(f"📋 Arquivo existe? {os.path.exists(env_path)}")
load_dotenv(env_path, override=True)

# Debug: mostra o que foi carregado
print(f"\n🔍 MINASTAXI_API_URL = {os.getenv('MINASTAXI_API_URL')}")
print(f"🔍 MINASTAXI_USER_ID = {os.getenv('MINASTAXI_USER_ID')}")
print()


def print_section(title):
    """Imprime separador de seção"""
    print("\n" + "=" * 80)
    print(f"📍 {title}")
    print("=" * 80)


def test_full_dispatch():
    """Testa dispatch completo de um email para MinasTaxi"""
    
    print_section("TESTE DE DISPATCH COMPLETO - EMAIL → MINASTAXI API")
    
    # ============================================================================
    # 1. EMAIL DE EXEMPLO (Email 2 - simples e completo)
    # ============================================================================
    print_section("1. EMAIL DE ENTRADA")
    
    email = EmailMessage(
        uid="test_dispatch_1",
        subject="PROGRAMAÇÃO DE TAXI amanhã 15:30h",
        from_="carlos.pereira@csn.com.br",
        date=datetime(2025, 9, 5, 19, 1),
        body="""Prezados, boa Noite!

Gentileza programar um TAXI amanhã 06/09/2025 15:30h

CSN DESTINHO BH

CC:20063

┌────────────────────────────┬────────┬──────────────┬──────┬──────┐
│ Harlle Jonathan da Rocha   │ MIP 0060│ 37998742019 │ CSN  │  BH  │
└────────────────────────────┴────────┴──────────────┴──────┴──────┘

Obrigado!"""
    )
    
    print(f"📧 Assunto: {email.subject}")
    print(f"📤 De: {email.from_}")
    print(f"📅 Data: {email.date}")
    print(f"📝 Corpo:\n{email.body}")
    
    # ============================================================================
    # 2. EXTRAÇÃO LLM
    # ============================================================================
    print_section("2. EXTRAÇÃO DE DADOS COM LLM (GPT-4)")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERRO: OPENAI_API_KEY não configurada no .env")
        return
    
    print("🤖 Inicializando LLM Extractor...")
    extractor = LLMExtractor(api_key=api_key)
    
    print("🔄 Extraindo dados do email...")
    extracted_data = extractor.extract_with_fallback(email.body)
    
    if not extracted_data:
        print("❌ ERRO: Falha na extração LLM")
        return
    
    print("✅ Dados extraídos com sucesso!")
    print(f"\n📊 DADOS EXTRAÍDOS:")
    print(f"   👤 Nome: {extracted_data.get('passenger_name')}")
    print(f"   📱 Telefone: {extracted_data.get('phone')}")
    print(f"   📍 Origem: {extracted_data.get('pickup_address')}")
    print(f"   🎯 Destino: {extracted_data.get('destination_address')}")
    print(f"   🕐 Horário: {extracted_data.get('pickup_time')}")
    print(f"   📝 Notas: {extracted_data.get('notes')}")
    
    # Cria objeto Order
    order = Order(
        email_id=email.uid,
        passenger_name=extracted_data.get('passenger_name'),
        phone=extracted_data.get('phone'),
        pickup_address=extracted_data.get('pickup_address'),
        dropoff_address=extracted_data.get('destination_address'),
        pickup_time=extracted_data.get('pickup_time'),
        raw_email_body=extracted_data.get('notes'),  # Notas vão aqui
        status=OrderStatus.EXTRACTED
    )
    
    # ============================================================================
    # 3. GEOCODING
    # ============================================================================
    print_section("3. GEOCODING - CONVERTENDO ENDEREÇOS EM COORDENADAS")
    
    use_google = os.getenv("GEOCODING_PROVIDER", "nominatim") == "google"
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY") if use_google else None
    
    print(f"🗺️  Provider: {'Google Maps' if use_google else 'Nominatim (OpenStreetMap)'}")
    
    geocoding_service = GeocodingService(
        use_google=use_google,
        google_api_key=google_api_key
    )
    
    print(f"\n🔍 Buscando coordenadas para origem: {order.pickup_address}")
    pickup_coords = geocoding_service.geocode_address(order.pickup_address)
    
    if pickup_coords:
        order.pickup_lat = pickup_coords[0]  # latitude
        order.pickup_lng = pickup_coords[1]  # longitude
        print(f"✅ Origem: ({order.pickup_lat}, {order.pickup_lng})")
    else:
        print(f"❌ ERRO: Não foi possível geocodificar origem")
        order.status = OrderStatus.MANUAL_REVIEW
        order.error_message = "Geocoding falhou para origem"
        return
    
    print(f"\n🔍 Buscando coordenadas para destino: {order.dropoff_address}")
    destination_coords = geocoding_service.geocode_address(order.dropoff_address)
    
    if destination_coords:
        order.dropoff_lat = destination_coords[0]  # latitude
        order.dropoff_lng = destination_coords[1]  # longitude
        print(f"✅ Destino: ({order.dropoff_lat}, {order.dropoff_lng})")
        order.status = OrderStatus.GEOCODED
    else:
        print(f"❌ ERRO: Não foi possível geocodificar destino")
        order.status = OrderStatus.MANUAL_REVIEW
        order.error_message = "Geocoding falhou para destino"
        return
    
    # ============================================================================
    # 4. DISPATCH PARA MINASTAXI
    # ============================================================================
    print_section("4. DISPATCH PARA MINASTAXI API")
    
    # Verifica credenciais
    api_url = os.getenv("MINASTAXI_API_URL")
    user_id = os.getenv("MINASTAXI_USER_ID")
    password = os.getenv("MINASTAXI_PASSWORD")
    auth_header = os.getenv("MINASTAXI_AUTH_HEADER")
    
    print(f"🔍 Debug - Variáveis carregadas:")
    print(f"   API_URL: {api_url}")
    print(f"   USER_ID: {user_id}")
    print(f"   PASSWORD: {'***' if password else None}")
    print(f"   AUTH_HEADER: {auth_header[:20] + '...' if auth_header else None}")
    print()
    
    if not all([api_url, user_id, password, auth_header]):
        print("❌ ERRO: Credenciais MinasTaxi não configuradas no .env")
        print("   Configure: MINASTAXI_API_URL, MINASTAXI_USER_ID, MINASTAXI_PASSWORD, MINASTAXI_AUTH_HEADER")
        return
    
    print(f"🚕 API URL: {api_url}")
    print(f"👤 User ID: {user_id}")
    print(f"🔑 Auth Header: {auth_header[:20]}...")
    
    print("\n📦 Montando payload para MinasTaxi...")
    minastaxi_client = MinasTaxiClient(
        api_url=api_url,
        user_id=user_id,
        password=password,
        auth_header=auth_header
    )
    
    print(f"\n📤 Enviando pedido para MinasTaxi API...")
    print(f"   Passageiro: {order.passenger_name}")
    print(f"   Telefone: {order.phone}")
    print(f"   Origem: ({order.pickup_lat}, {order.pickup_lng})")
    print(f"   Destino: ({order.dropoff_lat}, {order.dropoff_lng})")
    print(f"   Horário: {order.pickup_time}")
    
    try:
        # Pergunta confirmação antes de enviar
        print("\n" + "⚠️ " * 30)
        print("⚠️  ATENÇÃO: Isso enviará um pedido REAL para a API MinasTaxi!")
        print("⚠️ " * 30)
        confirmation = input("\n🤔 Deseja realmente enviar? (digite 'SIM' para confirmar): ")
        
        if confirmation.upper() != "SIM":
            print("\n❌ Cancelado pelo usuário. Nenhum pedido foi enviado.")
            return
        
        print("\n🚀 Enviando...")
        result = minastaxi_client.dispatch_order(order)
        
        if result and result.get('success'):
            order.status = OrderStatus.DISPATCHED
            order.minastaxi_order_id = result.get('ride_id')
            
            print_section("✅ SUCESSO - PEDIDO DESPACHADO!")
            print(f"🎉 Ride ID: {order.minastaxi_order_id}")
            print(f"📋 Status: {order.status.value}")
            
            if result.get('response'):
                print(f"\n📨 Resposta da API:")
                import json
                print(json.dumps(result['response'], indent=2, ensure_ascii=False))
        else:
            order.status = OrderStatus.FAILED
            order.error_message = result.get('error', 'Erro desconhecido')
            
            print_section("❌ FALHA NO DISPATCH")
            print(f"❌ Erro: {order.error_message}")
            
            if result.get('response'):
                print(f"\n📨 Resposta da API:")
                import json
                print(json.dumps(result['response'], indent=2, ensure_ascii=False))
    
    except Exception as e:
        order.status = OrderStatus.FAILED
        order.error_message = str(e)
        
        print_section("❌ ERRO DURANTE DISPATCH")
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # ============================================================================
    # 5. RESUMO FINAL
    # ============================================================================
    print_section("5. RESUMO FINAL DO TESTE")
    
    print(f"📧 Email ID: {order.email_id}")
    print(f"👤 Passageiro: {order.passenger_name}")
    print(f"📱 Telefone: {order.phone}")
    print(f"📍 Origem: {order.pickup_address}")
    print(f"   Coordenadas: ({order.pickup_lat}, {order.pickup_lng})")
    print(f"🎯 Destino: {order.dropoff_address}")
    print(f"   Coordenadas: ({order.dropoff_lat}, {order.dropoff_lng})")
    print(f"🕐 Horário: {order.pickup_time}")
    print(f"📝 Notas: {order.raw_email_body}")
    print(f"\n🚦 STATUS FINAL: {order.status.value}")
    
    if order.minastaxi_order_id:
        print(f"🎫  MinasTaxi Ride ID: {order.minastaxi_order_id}")
    
    if order.error_message:
        print(f"❌ Erro: {order.error_message}")
    
    print("\n" + "=" * 80)
    
    if order.status == OrderStatus.DISPATCHED:
        print("🎉 TESTE COMPLETO - PEDIDO DESPACHADO COM SUCESSO!")
    elif order.status == OrderStatus.FAILED:
        print("❌ TESTE COMPLETO - PEDIDO FALHOU NO DISPATCH")
    else:
        print(f"⚠️  TESTE COMPLETO - STATUS: {order.status.value}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_full_dispatch()
