"""
Teste End-to-End do Sistema de Automação de Táxi
Simula um pedido completo: Criação → Processamento → Despacho Mock → Notificação WhatsApp
"""
import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Adiciona diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.models.order import Order, OrderStatus
from src.services.llm_extractor import LLMExtractor
from src.services.geocoding_service import GeocodingService
from src.services.minastaxi_client import MinasTaxiClient
from src.services.whatsapp_notifier import WhatsAppNotifier
from src.services.database import DatabaseManager

def main():
    """Executa teste end-to-end do sistema."""
    
    # Carrega env
    load_dotenv()
    
    print("\n" + "=" * 70)
    print("🚖 TESTE END-TO-END - SISTEMA DE AUTOMAÇÃO DE TÁXI")
    print("=" * 70)
    
    # Inicializa serviços
    print("\n📦 Inicializando serviços...")
    
    db = DatabaseManager(os.getenv('DATABASE_PATH', 'data/taxi_orders.db'))
    
    geocoding = GeocodingService(
        google_api_key=os.getenv('GOOGLE_MAPS_API_KEY'),
        use_google=os.getenv('USE_GOOGLE_MAPS', 'false').lower() == 'true'
    )
    
    minastaxi = MinasTaxiClient(
        api_url=os.getenv('MINASTAXI_API_URL'),
        api_key=os.getenv('MINASTAXI_API_KEY'),
        timeout=int(os.getenv('MINASTAXI_TIMEOUT', 30)),
        retry_attempts=int(os.getenv('MINASTAXI_RETRY_ATTEMPTS', 3))
    )
    
    whatsapp = WhatsAppNotifier(
        api_url=os.getenv('EVOLUTION_API_URL'),
        api_key=os.getenv('EVOLUTION_API_KEY'),
        instance_name=os.getenv('EVOLUTION_INSTANCE_NAME')
    )
    
    print("✅ Serviços inicializados")
    
    # Cria pedido de teste
    print("\n" + "-" * 70)
    print("📝 ETAPA 1: Criando pedido de teste")
    print("-" * 70)
    
    pickup_time = datetime.now() + timedelta(hours=2)
    
    order = Order(
        email_id=f"TEST-{int(time.time())}",
        raw_email_content="Email de teste do sistema",
        passenger_name="Maria Silva",
        passenger_phone="31988887777",
        passenger_email="maria.silva@email.com",
        pickup_address="Avenida Afonso Pena, 1500, Belo Horizonte, MG",
        destination_address="Aeroporto Internacional de Confins, Confins, MG",
        pickup_time=pickup_time.isoformat(),
        notes="Cliente preferencial - Bagagens"
    )
    
    print(f"   Nome: {order.passenger_name}")
    print(f"   Telefone: {order.passenger_phone}")
    print(f"   Origem: {order.pickup_address}")
    print(f"   Destino: {order.destination_address}")
    print(f"   Horário: {pickup_time.strftime('%d/%m/%Y %H:%M')}")
    
    # Salva no banco
    order_id = db.create_order(order)
    print(f"✅ Pedido criado no banco (ID: {order_id})")
    
    # Geocoding
    print("\n" + "-" * 70)
    print("🗺️  ETAPA 2: Geocodificação de endereços")
    print("-" * 70)
    
    try:
        print("   Buscando coordenadas da origem...")
        order = geocoding.geocode_addresses(order)
        print(f"   ✅ Origem: ({order.pickup_latitude:.4f}, {order.pickup_longitude:.4f})")
        print(f"   ✅ Destino: ({order.destination_latitude:.4f}, {order.destination_longitude:.4f})")
        db.update_order(order_id, order)
    except Exception as e:
        print(f"   ❌ Erro no geocoding: {e}")
        return
    
    # Despacho para MinasTaxi (Mock)
    print("\n" + "-" * 70)
    print("🚕 ETAPA 3: Despachando para MinasTaxi API (MOCK)")
    print("-" * 70)
    
    try:
        print("   Enviando pedido para API...")
        result = minastaxi.dispatch_order(order)
        
        if result.get('success'):
            order.status = OrderStatus.DISPATCHED
            order.minastaxi_order_id = result.get('order_id')
            print(f"   ✅ Pedido despachado com sucesso!")
            print(f"   📋 Order ID: {result.get('order_id')}")
            print(f"   🚗 Motorista: {result.get('driver', {}).get('name')}")
            print(f"   🚙 Veículo: {result.get('driver', {}).get('vehicle')}")
            db.update_order(order_id, order)
        else:
            print(f"   ❌ Falha ao despachar: {result.get('error')}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao despachar: {e}")
        return
    
    # Notificação WhatsApp
    print("\n" + "-" * 70)
    print("📱 ETAPA 4: Enviando notificação via WhatsApp")
    print("-" * 70)
    
    enable_whatsapp = os.getenv('ENABLE_WHATSAPP_NOTIFICATIONS', 'false').lower() == 'true'
    
    if enable_whatsapp:
        try:
            print(f"   Enviando mensagem para {order.passenger_phone}...")
            whatsapp_result = whatsapp.send_message(
                name=order.passenger_name,
                phone=order.passenger_phone,
                destination=order.destination_address,
                status="Sucesso"
            )
            
            if whatsapp_result.get('success'):
                print(f"   ✅ WhatsApp enviado com sucesso!")
                print(f"   📲 Message ID: {whatsapp_result.get('message_id')}")
            else:
                print(f"   ⚠️  Falha ao enviar WhatsApp: {whatsapp_result.get('error')}")
        except Exception as e:
            print(f"   ⚠️  Erro ao enviar WhatsApp: {e}")
    else:
        print("   ⏭️  Notificações WhatsApp desabilitadas no .env")
    
    # Resumo final
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📊 Verifique os resultados:")
    print(f"   1. Banco de dados: {os.getenv('DATABASE_PATH')}")
    print(f"   2. Planilha Mock: data/agendamentos_minastaxi.xlsx")
    print(f"   3. WhatsApp do cliente: {order.passenger_phone}")
    print(f"   4. Logs: {os.getenv('LOG_FILE')}")
    print("\n💡 Dica: Abra a planilha Excel para ver o agendamento registrado!")
    print()

if __name__ == '__main__':
    main()
