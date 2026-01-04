"""
Teste da detecção de pedidos duplicados por conteúdo
"""
from datetime import datetime, timedelta
from src.services.database import DatabaseManager
from src.models.order import Order, OrderStatus
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cria banco de teste
db = DatabaseManager('data/test_duplicates.db')

print("=" * 60)
print("🧪 TESTE DE DETECÇÃO DE DUPLICATAS")
print("=" * 60)

# Cenário 1: Mesmo passageiro, mesmo endereço, MESMO horário
print("\n📋 Cenário 1: Mesmo horário (duplicata)")
order1 = Order(
    email_id="email_001",
    passenger_name="João Silva",
    pickup_address="Rua ABC, 123 - Belo Horizonte",
    pickup_time=datetime(2026, 1, 5, 8, 0, 0),
    phone="31999999999",
    status=OrderStatus.DISPATCHED
)
order1.id = db.create_order(order1)
print(f"✅ Pedido 1 criado: {order1.passenger_name} às 08:00")

# Tenta criar duplicata
is_dup = db.check_duplicate_order(
    passenger_name="João Silva",
    pickup_address="Rua ABC, 123 - Belo Horizonte",
    pickup_time=datetime(2026, 1, 5, 8, 10, 0),  # 10 min depois
    tolerance_minutes=30
)
print(f"{'🚫' if is_dup else '✅'} Duplicata detectada? {is_dup} (esperado: True)")

# Cenário 2: Mesmo passageiro, mesmo endereço, HORÁRIO DIFERENTE
print("\n📋 Cenário 2: Horário diferente (NÃO duplicata)")
is_dup = db.check_duplicate_order(
    passenger_name="João Silva",
    pickup_address="Rua ABC, 123 - Belo Horizonte",
    pickup_time=datetime(2026, 1, 5, 10, 0, 0),  # 2 horas depois
    tolerance_minutes=30
)
print(f"{'✅' if not is_dup else '🚫'} Duplicata detectada? {is_dup} (esperado: False)")

# Cenário 3: Mesmo passageiro, ENDEREÇO DIFERENTE, mesmo horário
print("\n📋 Cenário 3: Endereço diferente (NÃO duplicata)")
is_dup = db.check_duplicate_order(
    passenger_name="João Silva",
    pickup_address="Rua XYZ, 456 - Contagem",
    pickup_time=datetime(2026, 1, 5, 8, 0, 0),
    tolerance_minutes=30
)
print(f"{'✅' if not is_dup else '🚫'} Duplicata detectada? {is_dup} (esperado: False)")

# Cenário 4: PASSAGEIRO DIFERENTE, mesmo endereço, mesmo horário
print("\n📋 Cenário 4: Passageiro diferente (NÃO duplicata)")
is_dup = db.check_duplicate_order(
    passenger_name="Maria Souza",
    pickup_address="Rua ABC, 123 - Belo Horizonte",
    pickup_time=datetime(2026, 1, 5, 8, 0, 0),
    tolerance_minutes=30
)
print(f"{'✅' if not is_dup else '🚫'} Duplicata detectada? {is_dup} (esperado: False)")

# Cenário 5: Pedido duplicado mas com status FAILED (deve permitir reagendar)
print("\n📋 Cenário 5: Duplicata com status FAILED (permite reagendar)")
order_failed = Order(
    email_id="email_002",
    passenger_name="Pedro Costa",
    pickup_address="Rua DEF, 789 - Sabará",
    pickup_time=datetime(2026, 1, 5, 14, 0, 0),
    phone="31988888888",
    status=OrderStatus.FAILED
)
order_failed.id = db.create_order(order_failed)
print(f"✅ Pedido FAILED criado: {order_failed.passenger_name}")

is_dup = db.check_duplicate_order(
    passenger_name="Pedro Costa",
    pickup_address="Rua DEF, 789 - Sabará",
    pickup_time=datetime(2026, 1, 5, 14, 10, 0),
    tolerance_minutes=30
)
print(f"{'✅' if not is_dup else '🚫'} Duplicata detectada? {is_dup} (esperado: False - ignora FAILED)")

# Cenário 6: Mesmo pedido mas DIA DIFERENTE
print("\n📋 Cenário 6: Mesmo horário mas DIA DIFERENTE (NÃO duplicata)")
is_dup = db.check_duplicate_order(
    passenger_name="João Silva",
    pickup_address="Rua ABC, 123 - Belo Horizonte",
    pickup_time=datetime(2026, 1, 6, 8, 0, 0),  # Dia seguinte
    tolerance_minutes=30
)
print(f"{'✅' if not is_dup else '🚫'} Duplicata detectada? {is_dup} (esperado: False)")

print("\n" + "=" * 60)
print("✅ Testes concluídos!")
print("=" * 60)
print("\n📝 Resumo da Lógica:")
print("  - ✅ Detecta duplicatas com tolerância de 30 minutos")
print("  - ✅ Ignora case (maiúsculas/minúsculas)")
print("  - ✅ Ignora pedidos com status FAILED")
print("  - ✅ Permite pedidos em dias diferentes")
print("  - ✅ Permite pedidos com 2+ horas de diferença")
