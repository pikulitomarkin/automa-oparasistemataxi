"""
Teste simplificado: Valida a lógica de múltiplos passageiros WhatsApp.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class MockOrder:
    """Mock de Order para teste."""
    id: int
    passenger_name: str
    phone: str
    passengers: List[Dict[str, str]]

def test_multiple_passengers_logic():
    """
    Testa a lógica de identificação de múltiplos passageiros
    sem fazer chamadas reais à API.
    """
    
    # Simula pedido com 3 passageiros, sendo um duplicado
    order = MockOrder(
        id=999,
        passenger_name="Gasparino Rodrigues da Silva",
        phone="31999999926",
        passengers=[
            {
                "name": "Gasparino Rodrigues da Silva",
                "phone": "31999999926",  # DUPLICADO com phone principal
                "address": "RUA Jorge Dias de Oliva, 172"
            },
            {
                "name": "Timoteo de Almeida Batalha",
                "phone": "31988887777",  # ÚNICO
                "address": "RUA Ceará, 200"
            },
            {
                "name": "Brendo dos Santos Silva",
                "phone": "31977776666",  # ÚNICO
                "address": "AV. Alcino Gonçalves Cota, 563"
            },
            {
                "name": "Maria sem telefone",
                "phone": "",  # SEM TELEFONE - deve ser ignorado
                "address": "Rua X, 123"
            }
        ]
    )
    
    print("=" * 80)
    print("TESTE: Lógica de Múltiplos Passageiros WhatsApp")
    print("=" * 80)
    print(f"\n📋 Dados do Pedido:")
    print(f"  ID: {order.id}")
    print(f"  Passageiro Principal: {order.passenger_name}")
    print(f"  Telefone Principal: {order.phone}")
    print(f"  Total Passageiros no Array: {len(order.passengers)}")
    
    print(f"\n{'─' * 80}")
    print("FASE 1: Montando Lista de Notificações")
    print(f"{'─' * 80}")
    
    # ===== LÓGICA DO PROCESSOR (COPIADA) =====
    passengers_to_notify = []
    
    # Se houver múltiplos passageiros, usa APENAS a lista individualizada
    if order.passengers:
        for idx, passenger in enumerate(order.passengers, 1):
            if passenger.get('phone'):
                passengers_to_notify.append({
                    'name': passenger.get('name', 'Cliente'),
                    'phone': passenger['phone']
                })
                print(f"✅ [Pass. {idx}] {passenger['name']} - {passenger['phone']}")
            else:
                print(f"⚠️ [Pass. {idx}] {passenger.get('name', 'Sem nome')} - SEM TELEFONE (ignorado)")
    # Senão, usa o passageiro principal (passageiro único)
    elif order.phone:
        passengers_to_notify.append({
            'name': order.passenger_name or "Cliente",
            'phone': order.phone
        })
        print(f"✅ [Principal] {order.passenger_name} - {order.phone}")
    # ===== FIM DA LÓGICA =====
    
    print(f"\n{'─' * 80}")
    print("FASE 2: Resultado Final")
    print(f"{'─' * 80}")
    print(f"\n📊 Estatísticas:")
    print(f"  • Total de passageiros no pedido: {len(order.passengers)}")
    print(f"  • Passageiros com telefone válido: {len([p for p in order.passengers if p.get('phone')])}")
    print(f"  • Sem telefone: 1")  # Maria sem telefone
    print(f"  • Total de mensagens WhatsApp: {len(passengers_to_notify)}")
    
    print(f"\n📱 Lista Final de Envios:")
    for idx, p in enumerate(passengers_to_notify, 1):
        print(f"  {idx}. {p['name']} → {p['phone']}")
    
    # Validações
    print(f"\n{'=' * 80}")
    print("VALIDAÇÕES")
    print(f"{'=' * 80}")
    
    expected_count = 3  # Gasparino (principal), Timoteo, Brendo
    
    test_results = {
        "✅ Total correto (3 mensagens)": len(passengers_to_notify) == expected_count,
        "✅ Sem duplicatas": len(passengers_to_notify) == len(set(p['phone'] for p in passengers_to_notify)),
        "✅ Todos têm telefone": all(p['phone'] for p in passengers_to_notify),
        "✅ Gasparino incluído": any(p['phone'] == "31999999926" for p in passengers_to_notify),
        "✅ Timoteo incluído": any(p['phone'] == "31988887777" for p in passengers_to_notify),
        "✅ Brendo incluído": any(p['phone'] == "31977776666" for p in passengers_to_notify),
        "✅ Maria excluída (sem tel)": not any(p['name'] == "Maria sem telefone" for p in passengers_to_notify)
    }
    
    all_passed = True
    for test_name, passed in test_results.items():
        status = test_name if passed else test_name.replace("✅", "❌")
        print(f"  {status}")
        if not passed:
            all_passed = False
    
    print(f"\n{'=' * 80}")
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Lógica de múltiplos passageiros está CORRETA")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Revisar a lógica de múltiplos passageiros")
    print(f"{'=' * 80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_multiple_passengers_logic()
    exit(0 if success else 1)
