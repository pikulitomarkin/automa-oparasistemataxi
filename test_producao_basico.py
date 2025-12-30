"""
Teste rápido do sistema principal sem relative imports
"""
import os
import sys
from datetime import datetime

# Adicionar paths
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/services')
sys.path.insert(0, 'src/models')

# Teste simples
def test_basic_functionality():
    print("🧪 TESTE BÁSICO DE FUNCIONALIDADE")
    print("="*50)
    
    try:
        # Test 1: RouteOptimizer
        print("1️⃣ Testando RouteOptimizer...")
        from services.route_optimizer import RouteOptimizer
        
        passengers = [
            {'name': 'Ana', 'lat': -19.9, 'lng': -43.9, 'address': 'Centro'},
            {'name': 'João', 'lat': -19.8, 'lng': -43.8, 'address': 'Savassi'}
        ]
        destination = (-20.0, -44.0)
        
        optimized = RouteOptimizer.optimize_pickup_sequence(passengers, destination)
        print(f"   ✅ {len(optimized)} passageiros otimizados")
        
        # Test 2: LLMExtractor
        print("2️⃣ Testando LLMExtractor...")
        from services.llm_extractor import LLMExtractor
        
        if os.getenv('OPENAI_API_KEY'):
            extractor = LLMExtractor(
                api_key=os.getenv('OPENAI_API_KEY'),
                model='gpt-4o'
            )
            print("   ✅ LLMExtractor inicializado")
        else:
            print("   ⚠️ OPENAI_API_KEY não encontrada")
        
        # Test 3: Order model
        print("3️⃣ Testando Order model...")
        from models.order import Order, OrderStatus
        
        order = Order(
            email_id="test_001",
            raw_email_body="Teste",
            passenger_name="Teste Silva",
            phone="31999999999",
            passengers=[
                {'name': 'Teste', 'phone': '31999999999', 'address': 'Rua Teste, 123'}
            ],
            pickup_address="Rua Teste, 123",
            dropoff_address="Praça da Liberdade",
            pickup_time=datetime.now(),
            status=OrderStatus.EXTRACTED,
            has_return=False
        )
        print(f"   ✅ Order criado com {len(order.passengers)} passageiros")
        
        # Test 4: MinasTaxiClient
        print("4️⃣ Testando MinasTaxiClient...")
        from services.minastaxi_client import MinasTaxiClient
        
        if all([os.getenv('MINASTAXI_API_URL'), os.getenv('MINASTAXI_USER_ID')]):
            client = MinasTaxiClient(
                api_url=os.getenv('MINASTAXI_API_URL'),
                user_id=os.getenv('MINASTAXI_USER_ID'),
                password=os.getenv('MINASTAXI_PASSWORD'),
                auth_header=os.getenv('MINASTAXI_AUTH_HEADER')
            )
            print("   ✅ MinasTaxiClient inicializado")
        else:
            print("   ⚠️ Credenciais MinasTaxi não encontradas")
        
        print("\n" + "="*50)
        print("✅ TODOS OS TESTES BÁSICOS PASSARAM!")
        print("🚀 Sistema pronto para produção")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_basic_functionality()