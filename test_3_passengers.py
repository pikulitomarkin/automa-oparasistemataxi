"""
Teste real com 3 passageiros para validar API MinasTaxi
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.llm_extractor import LLMExtractor
from src.services.geocoding_service import GeocodingService
from src.services.minastaxi_client import MinasTaxiClient
from src.services.route_optimizer import RouteOptimizer
from src.models.order import Order, OrderStatus

def test_3_passengers():
    """Testa envio de 3 passageiros para API MinasTaxi"""
    
    print("\n" + "="*60)
    print("🧪 TESTE: 3 PASSAGEIROS - API MINASTAXI")
    print("="*60)
    
    # Email simulado com 3 passageiros
    email_body = """
    Assunto: Novo Agendamento
    
    Data: 30/12/2025
    Horário de chegada DELP: 08:00
    
    Passageiros:
    1. João Silva - (31) 98888-1111 - Rua das Flores, 100, Belo Horizonte, MG
    2. Maria Santos - (31) 98888-2222 - Avenida Paulista, 200, Belo Horizonte, MG
    3. Pedro Costa - (31) 98888-3333 - Rua Rio de Janeiro, 300, Belo Horizonte, MG
    
    Destino: DELP - Delegacia de Polícia
    Centro de custo: 1.07002.07.001
    """
    
    try:
        # 1. Extrair dados com LLM
        print("\n📝 Passo 1: Extraindo dados com LLM...")
        extractor = LLMExtractor(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4o')
        )
        extracted_data = extractor.extract_order_data(email_body)
        
        if not extracted_data:
            print("❌ Falha na extração LLM")
            return
        
        print("✅ Dados extraídos:")
        print(f"   • Passageiros: {len(extracted_data.get('passengers', []))}")
        print(f"   • Horário coleta: {extracted_data.get('pickup_time')}")
        print(f"   • Origem: {extracted_data.get('pickup_address')}")
        print(f"   • Destino: {extracted_data.get('dropoff_address')}")
        
        for idx, p in enumerate(extracted_data.get('passengers', []), 1):
            print(f"   {idx}. {p.get('name')} - {p.get('phone')}")
        
        # 2. Criar Order
        print("\n📦 Passo 2: Criando Order...")
        order = Order(
            email_id="test_3pass_001",
            raw_email_body=email_body,
            passenger_name=extracted_data.get('passenger_name'),
            phone=extracted_data.get('phone'),
            passengers=extracted_data.get('passengers', []),
            pickup_address=extracted_data.get('pickup_address'),
            dropoff_address=extracted_data.get('dropoff_address'),
            pickup_time=datetime.fromisoformat(extracted_data['pickup_time']),
            status=OrderStatus.EXTRACTED
        )
        print("✅ Order criado")
        
        # 3. Geocoding - TODOS os endereços dos passageiros
        print("\n🌍 Passo 3: Geocoding endereços individuais...")
        geocoder = GeocodingService(
            use_google=os.getenv('USE_GOOGLE_MAPS', 'false').lower() == 'true',
            google_api_key=os.getenv('GOOGLE_MAPS_API_KEY')
        )
        
        # Geocoding destino primeiro
        destination_coords = None
        if order.dropoff_address:
            dropoff_coords = geocoder.geocode_address(order.dropoff_address)
            if dropoff_coords:
                order.dropoff_lat, order.dropoff_lng = dropoff_coords
                destination_coords = dropoff_coords
                print(f"✅ Destino: {order.dropoff_lat}, {order.dropoff_lng}")
        
        # Geocodificar endereço de cada passageiro
        for idx, passenger in enumerate(order.passengers):
            print(f"🔍 Geocodificando {passenger['name']}: {passenger['address']}")
            coords = geocoder.geocode_address(passenger['address'])
            if coords:
                passenger['lat'] = coords[0]
                passenger['lng'] = coords[1]
                print(f"✅ {passenger['name']}: {coords[0]}, {coords[1]}")
            else:
                print(f"❌ Falha geocoding para {passenger['name']}")
        
        # 4. OTIMIZAÇÃO DE ROTA
        print("\n🎯 Passo 4: Otimizando rota de coleta...")
        optimized_passengers = RouteOptimizer.optimize_pickup_sequence(
            order.passengers, 
            destination_coords
        )
        order.passengers = optimized_passengers
        
        print("✅ Rota otimizada:")
        for idx, p in enumerate(optimized_passengers, 1):
            if destination_coords and 'lat' in p:
                dist = RouteOptimizer.calculate_distance((p['lat'], p['lng']), destination_coords)
                print(f"   {idx}. {p['name']} (dist destino: {dist:.1f}km)")
            else:
                print(f"   {idx}. {p['name']}")
        
        # Usar primeiro endereço como referência para order.pickup_*
        if order.passengers and 'lat' in order.passengers[0]:
            order.pickup_lat = order.passengers[0]['lat']
            order.pickup_lng = order.passengers[0]['lng']
            # Atualizar pickup_address para múltiplas paradas
            addresses = [p['address'] for p in order.passengers]
            order.pickup_address = f"Múltiplas paradas: {' → '.join(addresses[:3])}" + ("..." if len(addresses) > 3 else "")
        else:
            pickup_coords = geocoder.geocode_address(order.pickup_address)
            if not pickup_coords:
                print(f"❌ Falha ao geocodificar origem: {order.pickup_address}")
                return
            order.pickup_lat, order.pickup_lng = pickup_coords
        
        print(f"🎯 Coordenada de referência: {order.pickup_lat}, {order.pickup_lng}")
        
        order.status = OrderStatus.GEOCODED
        
        # 5. Confirmar antes de enviar
        print("\n" + "="*60)
        print("📋 DADOS PRONTOS PARA ENVIO:")
        print("="*60)
        print(f"Passageiros: {len(order.passengers)} (rota otimizada)")
        for idx, p in enumerate(order.passengers, 1):
            print(f"  {idx}. {p['name']}")
            print(f"     Tel: {p['phone']}")
            print(f"     End: {p['address']}")
            if 'lat' in p and 'lng' in p:
                print(f"     GPS: {p['lat']}, {p['lng']}")
        
        print(f"\nRota: {order.pickup_address}ckup_address)
            if not pickup_coords:
                print(f"❌ Falha ao geocodificar origem: {order.pickup_address}")
                return
            order.pickup_lat, order.pickup_lng = pickup_coords
        
        print(f"🎯 Coordenada de referência: {order.pickup_lat}, {order.pickup_lng}")
        
        order.status = OrderStatus.GEOCODED
        
        # 4. Confirmar antes de enviar
        print("\n" + "="*60)
        print("📋 DADOS PRONTOS PARA ENVIO:")
        print("="*60)
        print("Passageiros: {len(order.passengers)}")
        for idx, p in enumerate(order.passengers, 1):
            print(f"  {idx}. {p['name']}")
            print(f"     Tel: {p['phone']}")
            print(f"     End: {p['address']}")
            if 'lat' in p and 'lng' in p:
                print(f"     GPS: {p['lat']}, {p['lng']}")
        print(f"\nOrigem: {order.pickup_address} (referência)")
        print(f"Destino: {order.dropoff_address}")
        print(f"Horário: {order.pickup_time.strftime('%d/%m/%Y %H:%M')}")
        print(f"Coordenadas referência: {order.pickup_lat}, {order.pickup_lng}")
        print(f"Coordenadas destino: {order.dropoff_lat}, {order.dropoff_lng}")
        print("="*60)
        
        confirma = input("\n🚨 CONFIRMA ENVIO PARA API MINASTAXI? (sim/não): ").strip().lower()
        
        if confirma != 'sim':
            print("\n❌ Envio cancelado pelo usuário")
            return
        
            api_url=os.getenv('MINASTAXI_API_URL'),
            user_id=os.getenv('MINASTAXI_USER_ID'),
            password=os.getenv('MINASTAXI_PASSWORD'),
            auth_header=os.getenv('MINASTAXI_AUTH_HEADER'),
            timeout=int(os.getenv('MINASTAXI_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('MINASTAXI_RETRY_ATTEMPTS', '3'))
        6. Dispatch para MinasTaxi
        print("\n🚀 Passo 5MinasTaxi
        print("\n🚀 Passo 4: Enviando para API MinasTaxi...")
        client = MinasTaxiClient()
        response = client.dispatch_order(order)
        
        print("\n" + "="*60)
        print("✅ SUCESSO! PEDIDO ENVIADO")
        print("="*60)
        print(f"Response: {response}")
        
        if response.get('order_id'):
            print(f"🎫 Order ID: {response['order_id']}")
        
        order.status = OrderStatus.DISPATCHED
        order.minastaxi_order_id = response.get('order_id')
        
        print("\n✅ Teste concluído com sucesso!")
        print(f"Status final: {order.status.value}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_3_passengers()
