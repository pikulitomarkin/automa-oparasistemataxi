"""
Teste completo do sistema integrado com múltiplos passageiros
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processor import TaxiOrderProcessor
from src.services.email_reader import EmailMessage

def test_complete_system():
    """Teste completo do sistema com múltiplos passageiros"""
    
    print("\n" + "="*70)
    print("🧪 TESTE COMPLETO DO SISTEMA - MÚLTIPLOS PASSAGEIROS")
    print("="*70)
    
    # Email simulado com múltiplos passageiros
    email_content = """
    Assunto: PROGRAMAÇÃO
    
    Data: 30/12/2025
    Horário de chegada DELP: 08:30
    
    Passageiros:
    1. Ana Silva - (31) 99999-1111 - Rua Tupinambás, 500, Centro, Belo Horizonte, MG
    2. Carlos Santos - (31) 99999-2222 - Avenida Brasil, 1000, Centro, Belo Horizonte, MG  
    3. Maria Costa - (31) 99999-3333 - Rua da Bahia, 200, Centro, Belo Horizonte, MG
    4. João Oliveira - (31) 99999-4444 - Praça da Liberdade, 10, Funcionários, Belo Horizonte, MG
    
    Destino: DELP - Delegacia Especializada em Proteção à Criança e ao Adolescente
    Centro de custo: 1.07002.07.001
    Observações: Grupo CSN - Transporte oficial
    """
    
    try:
        # Criar email mock
        email = EmailMessage(
            uid="test_complete_001",
            subject="PROGRAMAÇÃO",
            from_addr="test@exemplo.com",
            body=email_content,
            date=datetime.now()
        )
        
        # Inicializar processor
        print("🚀 Inicializando TaxiOrderProcessor...")
        processor = TaxiOrderProcessor()
        
        # Processar email
        print("📧 Processando email com múltiplos passageiros...")
        order = processor.process_email(email)
        
        print("\n" + "="*70)
        print("📊 RESULTADO DO PROCESSAMENTO:")
        print("="*70)
        
        if order:
            print(f"✅ Order ID: {order.id}")
            print(f"✅ Status: {order.status.value}")
            print(f"✅ Passageiros: {len(order.passengers) if order.passengers else 1}")
            
            if order.passengers:
                print("\n📋 ROTA OTIMIZADA:")
                for idx, p in enumerate(order.passengers, 1):
                    print(f"  {idx}. {p.get('name')} - {p.get('address')}")
            
            print(f"\n🎯 Origem: {order.pickup_address}")
            print(f"🎯 Destino: {order.dropoff_address}")
            print(f"🕐 Horário: {order.pickup_time}")
            print(f"🗺️  Coordenadas origem: {order.pickup_lat}, {order.pickup_lng}")
            print(f"🗺️  Coordenadas destino: {order.dropoff_lat}, {order.dropoff_lng}")
            
            if order.minastaxi_order_id:
                print(f"🎫 MinasTaxi Order ID: {order.minastaxi_order_id}")
            
            if order.error_message:
                print(f"⚠️  Erro: {order.error_message}")
            
            print(f"\n✅ TESTE CONCLUÍDO - Status final: {order.status.value}")
            
        else:
            print("❌ Falha no processamento - Order não retornado")
            
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_system()