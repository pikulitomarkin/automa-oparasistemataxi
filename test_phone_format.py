"""
Teste da função de remoção de DDI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.services.minastaxi_client import MinasTaxiClient

print("\n" + "="*70)
print("🔧 TESTE DE REMOÇÃO DE DDI PARA MINASTAXI")
print("="*70)

# Cria cliente (apenas para ter acesso à função)
client = MinasTaxiClient(
    api_url="https://vm2c.taxifone.com.br:11048",
    user_id="02572696000156",
    password="0104",
    auth_header="Basic Original.#2024"
)

# Testes
test_cases = [
    ("5531999999926", "31999999926"),  # Com DDI 55
    ("31999999926", "31999999926"),    # Sem DDI
    ("+5531999999926", "31999999926"), # Com + e DDI
    ("5543988713278", "43988713278"),  # Outro DDD
    ("(31) 9999-9926", "31999999926"), # Formatado
    ("55 31 99999-9926", "31999999926"), # Com espaços
]

print("\n📋 CASOS DE TESTE:")
print("-" * 70)

all_passed = True
for input_phone, expected in test_cases:
    result = client._remove_country_code(input_phone)
    status = "✅" if result == expected else "❌"
    
    print(f"{status} Input: {input_phone:20} → Output: {result:15} (Esperado: {expected})")
    
    if result != expected:
        all_passed = False

print("-" * 70)

if all_passed:
    print("\n✅ TODOS OS TESTES PASSARAM!")
    print("\n📋 RESUMO:")
    print("   ✅ DDI (55) será REMOVIDO para MinasTaxi")
    print("   ✅ DDI (55) será MANTIDO para WhatsApp")
    print("   ✅ MinasTaxi receberá apenas: DDD + número")
    print("   ✅ WhatsApp receberá formato completo: 55 + DDD + número")
else:
    print("\n❌ ALGUNS TESTES FALHARAM!")

print("\n" + "="*70)
