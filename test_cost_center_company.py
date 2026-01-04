"""
Teste rápido: validação de centro de custo e detecção de empresa
"""
import re


def extract_cost_center(notes: str) -> str:
    """Extrai centro de custo das observações"""
    if not notes:
        return None
    
    # Padrão: CC: 12345 ou CC:12345
    match = re.search(r'CC\s*:\s*(\d+)', notes, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Padrão: CENTRO DE CUSTO 1.07002.07.001
    match = re.search(r'CENTRO DE CUSTO\s*([\d.]+)', notes, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Padrão: sequência numérica com pontos (ex: 1.07002.07.001)
    match = re.search(r'\b(\d+\.\d+\.\d+\.\d+)\b', notes)
    if match:
        return match.group(1)
    
    return None


def detect_company(destination: str) -> str:
    """Detecta empresa com base no destino"""
    if not destination:
        return None
    
    destination_upper = destination.upper()
    
    # DELP - Delegacia Especializada
    if "DELP" in destination_upper or "DELEGACIA" in destination_upper:
        return "DELP"
    
    return None


# TESTES
print("=" * 60)
print("🧪 TESTES DE EXTRAÇÃO")
print("=" * 60)

# Teste 1: Centro de custo formato "CC:"
test_cases = [
    ("CC: 20086", "20086"),
    ("CC:20086", "20086"),
    ("CENTRO DE CUSTO 1.07002.07.001", "1.07002.07.001"),
    ("Passageiro com 1.07002.07.001 para DELP", "1.07002.07.001"),
    ("CC: 20063, Retorno programado", "20063"),
]

print("\n📊 Centro de Custo:")
for notes, expected in test_cases:
    result = extract_cost_center(notes)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{notes[:40]}...' → {result} (esperado: {expected})")

# Teste 2: Detecção de empresa
company_tests = [
    ("DELP - Delegacia Especializada", "DELP"),
    ("Delp Engenharia Vespasiano", "DELP"),
    ("Delegacia de Polícia - Centro", "DELP"),
    ("Av. das Nações, 999 - Vespasiano", None),
    ("Aeroporto de Confins", None),
]

print("\n🏢 Detecção de Empresa:")
for destination, expected in company_tests:
    result = detect_company(destination)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{destination}' → {result} (esperado: {expected})")

print("\n" + "=" * 60)
print("✅ Testes concluídos!")
print("=" * 60)
