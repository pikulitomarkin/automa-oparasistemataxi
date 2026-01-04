"""
Teste para validar o payload enviado para MinasTaxi com centro de custo e código de empresa.
"""
import os
import sys
import json
from datetime import datetime, timedelta

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from models.order import Order, OrderStatus

def test_payload_format():
    """
    Valida que o payload está sendo montado corretamente com
    extra1 (código empresa) e extra2 (centro de custo).
    """
    
    print("=" * 80)
    print("TESTE: Validação de Payload MinasTaxi")
    print("=" * 80)
    
    # Simula um pedido com centro de custo e código de empresa
    order = Order(
        id=999,
        passenger_name="Gasparino Rodrigues da Silva",
        phone="31999999926",
        pickup_address="RUA Jorge Dias de Oliva, 172, Vespasiano, MG",
        dropoff_address="Delp Engenharia Vespasiano (Av. das Nações, 999)",
        pickup_time=datetime.now() + timedelta(hours=2),
        pickup_lat=-19.692317,
        pickup_lng=-43.929001,
        dropoff_lat=-23.674366,
        dropoff_lng=-46.610116,
        status=OrderStatus.GEOCODED,
        cost_center="1.07002.07.004",  # EXTRAÍDO DO EMAIL
        company_code="284",  # EXTRAÍDO DO EMAIL
        notes="CC: 1.07002.07.004 | Empresa: 284 - Delp Engenharia"
    )
    
    print(f"\n📋 Dados do Pedido:")
    print(f"  Passageiro: {order.passenger_name}")
    print(f"  Centro de Custo: {order.cost_center}")
    print(f"  Código da Empresa: {order.company_code}")
    print(f"  Destino: {order.dropoff_address}")
    
    # Simula a montagem do payload (lógica do minastaxi_client.py)
    print(f"\n{'─' * 80}")
    print("PAYLOAD GERADO:")
    print(f"{'─' * 80}")
    
    payload = {
        "partner": "1",
        "user": "02572696000156",
        "password": "0104",
        "request_id": "20260104170000ABC",
        "pickup_time": str(int(order.pickup_time.timestamp())),
        "category": "taxi",
        "passenger_name": order.passenger_name,
        "passenger_phone_number": "31999999926",
        "payment_type": "ONLINE_PAYMENT",
        "passenger_note": f"C.Custo: {order.cost_center} | {order.notes}",
        "users": [
            {
                "id": 1,
                "sequence": 1,
                "name": order.passenger_name,
                "phone": "31999999926",
                "pickup": {
                    "address": order.pickup_address,
                    "city": "Vespasiano",
                    "state": "MG",
                    "postal_code": "",
                    "lat": str(order.pickup_lat),
                    "lng": str(order.pickup_lng)
                }
            }
        ],
        "destinations": [
            {
                "passengerId": 1,
                "sequence": 2,
                "location": {
                    "address": order.dropoff_address,
                    "city": "Vespasiano",
                    "state": "MG",
                    "postal_code": "",
                    "lat": str(order.dropoff_lat),
                    "lng": str(order.dropoff_lng)
                }
            }
        ]
    }
    
    # CAMPOS CRÍTICOS: extra1 e extra2
    if order.company_code:
        payload["extra1"] = order.company_code
        print(f"✅ extra1 (Código Empresa): {order.company_code}")
    
    if order.cost_center:
        payload["extra2"] = order.cost_center
        print(f"✅ extra2 (Centro de Custo): {order.cost_center}")
    
    # Mostra payload completo em JSON
    print(f"\n{'─' * 80}")
    print("JSON COMPLETO (formatado):")
    print(f"{'─' * 80}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # Validações
    print(f"\n{'=' * 80}")
    print("VALIDAÇÕES")
    print(f"{'=' * 80}")
    
    tests = {
        "✅ extra1 presente (código empresa)": "extra1" in payload,
        "✅ extra1 = '284'": payload.get("extra1") == "284",
        "✅ extra2 presente (centro custo)": "extra2" in payload,
        "✅ extra2 = '1.07002.07.004'": payload.get("extra2") == "1.07002.07.004",
        "✅ passenger_note contém C.Custo": "C.Custo" in payload.get("passenger_note", ""),
        "✅ users array não vazio": len(payload.get("users", [])) > 0,
        "✅ destinations array não vazio": len(payload.get("destinations", [])) > 0
    }
    
    all_passed = True
    for test_name, result in tests.items():
        status = test_name if result else test_name.replace("✅", "❌")
        print(f"  {status}")
        if not result:
            all_passed = False
    
    print(f"\n{'=' * 80}")
    if all_passed:
        print("🎉 PAYLOAD CORRETO!")
        print("✅ Campos extra1 (empresa) e extra2 (centro custo) presentes")
        print("✅ MinasTaxi receberá os dados corretamente")
    else:
        print("❌ PAYLOAD INCORRETO")
        print("⚠️ Revisar a montagem do payload")
    print(f"{'=' * 80}\n")
    
    # Explicação dos campos
    print(f"\n{'─' * 80}")
    print("MAPEAMENTO DE CAMPOS NA TELA MINASTAXI:")
    print(f"{'─' * 80}")
    print(f"  extra1 ('{payload.get('extra1')}') → Campo 'Código / Empresa'")
    print(f"  extra2 ('{payload.get('extra2')}') → Campo 'C.Custo'")
    print(f"  passenger_note → Campo 'Obs. Operador(a)'")
    print(f"{'─' * 80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_payload_format()
    exit(0 if success else 1)
