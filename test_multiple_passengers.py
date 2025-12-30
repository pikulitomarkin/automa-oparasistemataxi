"""
Teste de Múltiplos Passageiros - API MinasTaxi
Valida até quantos passageiros a API aceita por solicitação
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.minastaxi_client import MinasTaxiClient

# Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), '.env')
for key in ['MINASTAXI_API_URL', 'MINASTAXI_USER_ID', 'MINASTAXI_PASSWORD', 'MINASTAXI_AUTH_HEADER']:
    if key in os.environ:
        del os.environ[key]
load_dotenv(env_path, override=True)


def test_multiple_passengers():
    """Testa API MinasTaxi com diferentes quantidades de passageiros"""
    
    print("=" * 80)
    print("🧪 TESTE: MÚLTIPLOS PASSAGEIROS - API MINASTAXI")
    print("=" * 80)
    print()
    
    # Configuração
    api_url = os.getenv('MINASTAXI_API_URL')
    user_id = os.getenv('MINASTAXI_USER_ID')
    password = os.getenv('MINASTAXI_PASSWORD')
    auth_header = os.getenv('MINASTAXI_AUTH_HEADER')
    
    print("🔑 CREDENCIAIS:")
    print(f"   API URL: {api_url}")
    print(f"   User ID: {user_id}")
    print(f"   Auth Header: {auth_header[:20]}...")
    print()
    
    # Inicializa cliente
    print("🚀 Inicializando cliente MinasTaxi...")
    client = MinasTaxiClient(
        api_url=api_url,
        user_id=user_id,
        password=password,
        auth_header=auth_header
    )
    print("✅ Cliente inicializado")
    print()
    
    # Dados base
    base_pickup = {
        "address": "CSN Mineração, Congonhas, MG",
        "lat": "-20.4872495",
        "lng": "-43.8950818",
        "city": "Congonhas",
        "state": "MG",
        "postal_code": ""
    }
    
    destination = {
        "address": "Belo Horizonte, MG",
        "lat": "-19.9227318",
        "lng": "-43.9450948",
        "city": "Belo Horizonte",
        "state": "MG",
        "postal_code": ""
    }
    
    # Testa com diferentes quantidades
    test_cases = [
        {"count": 1, "passengers": [
            {"name": "João Silva", "phone": "31999998888"}
        ]},
        {"count": 2, "passengers": [
            {"name": "João Silva", "phone": "31999998888"},
            {"name": "Maria Santos", "phone": "31988887777"}
        ]},
        {"count": 3, "passengers": [
            {"name": "João Silva", "phone": "31999998888"},
            {"name": "Maria Santos", "phone": "31988887777"},
            {"name": "Pedro Costa", "phone": "31977776666"}
        ]},
        {"count": 5, "passengers": [
            {"name": "João Silva", "phone": "31999998888"},
            {"name": "Maria Santos", "phone": "31988887777"},
            {"name": "Pedro Costa", "phone": "31977776666"},
            {"name": "Ana Oliveira", "phone": "31966665555"},
            {"name": "Carlos Souza", "phone": "31955554444"}
        ]}
    ]
    
    results = []
    
    print("=" * 80)
    print("🧪 INICIANDO TESTES")
    print("=" * 80)
    print()
    
    for test_case in test_cases:
        count = test_case["count"]
        passengers = test_case["passengers"]
        
        print("-" * 80)
        print(f"📊 TESTE COM {count} PASSAGEIRO(S)")
        print("-" * 80)
        print()
        
        # Monta payload
        unix_time = int(datetime(2025, 9, 6, 15, 30, 0).timestamp())
        request_id = f"test_multi_passengers_{count}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        users = []
        for idx, passenger in enumerate(passengers, 1):
            users.append({
                "id": idx,
                "sequence": idx,
                "name": passenger["name"],
                "phone": passenger["phone"],
                "pickup": base_pickup
            })
        
        payload = {
            "partner": "1",
            "user": user_id,
            "password": password,
            "request_id": request_id,
            "date_ride": unix_time,
            "passengers_no": count,
            "users": users,
            "destinations": [
                {
                    "address": destination["address"],
                    "lat": destination["lat"],
                    "lng": destination["lng"]
                }
            ],
            "origin": {
                "address": base_pickup["address"],
                "lat": base_pickup["lat"],
                "lng": base_pickup["lng"]
            }
        }
        
        print(f"👥 Passageiros:")
        for user in users:
            print(f"   {user['id']}. {user['name']} - {user['phone']}")
        print()
        
        print("📦 Payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print()
        
        # Pergunta confirmação
        confirm = input(f"❓ Enviar requisição com {count} passageiro(s)? (SIM para confirmar): ").strip().upper()
        
        if confirm != "SIM":
            print(f"⏭️  Teste com {count} passageiro(s) pulado")
            print()
            results.append({
                "count": count,
                "status": "SKIPPED",
                "message": "Usuário pulou o teste"
            })
            continue
        
        # Envia requisição
        try:
            print(f"📤 Enviando para MinasTaxi API...")
            
            endpoint = f"{api_url}/rideCreate"
            response = client.session.post(
                endpoint,
                json=payload,
                headers=client.headers,
                timeout=client.timeout,
                verify=False
            )
            
            print(f"📥 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCESSO!")
                print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                ride_id = data.get('ride_id') or data.get('id')
                results.append({
                    "count": count,
                    "status": "SUCCESS",
                    "ride_id": ride_id,
                    "response": data
                })
            else:
                error_data = response.text
                print(f"❌ ERRO: {response.status_code}")
                print(f"   Response: {error_data}")
                
                results.append({
                    "count": count,
                    "status": "ERROR",
                    "status_code": response.status_code,
                    "error": error_data
                })
                
        except Exception as e:
            print(f"💥 EXCEÇÃO: {type(e).__name__}")
            print(f"   Mensagem: {str(e)}")
            
            results.append({
                "count": count,
                "status": "EXCEPTION",
                "error": str(e)
            })
        
        print()
    
    # Resumo final
    print("=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    print()
    
    for result in results:
        count = result["count"]
        status = result["status"]
        
        if status == "SUCCESS":
            ride_id = result.get("ride_id", "N/A")
            print(f"✅ {count} passageiro(s): ACEITO (Ride ID: {ride_id})")
        elif status == "ERROR":
            status_code = result.get("status_code", "N/A")
            print(f"❌ {count} passageiro(s): REJEITADO (Status: {status_code})")
        elif status == "EXCEPTION":
            print(f"💥 {count} passageiro(s): EXCEÇÃO ({result.get('error', 'N/A')[:50]}...)")
        else:
            print(f"⏭️  {count} passageiro(s): PULADO")
    
    print()
    print("=" * 80)
    
    # Determina limite
    successful_counts = [r["count"] for r in results if r["status"] == "SUCCESS"]
    
    if successful_counts:
        max_passengers = max(successful_counts)
        print(f"🎯 LIMITE CONFIRMADO: Até {max_passengers} passageiro(s) aceitos")
    else:
        print("⚠️  Nenhum teste bem-sucedido. Verifique as credenciais ou API.")
    
    print("=" * 80)


if __name__ == "__main__":
    test_multiple_passengers()
