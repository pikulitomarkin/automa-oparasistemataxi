"""
Teste do novo Evolution API deployment
"""
import requests
import json

BASE_URL = "https://evolution-api-production-98d2.up.railway.app"
API_KEY = "minas2025taxi2026automacao"
INSTANCE_NAME = "instanciateste"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 60)
print("TESTE EVOLUTION API - NOVO DEPLOY")
print("=" * 60)

# 1. Teste de conectividade
print("\n1️⃣ Testando conectividade...")
try:
    response = requests.get(f"{BASE_URL}/", headers=headers, timeout=10)
    print(f"✅ Status: {response.status_code}")
    print(f"📄 Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Erro: {e}")

# 2. Listar instâncias
print("\n2️⃣ Listando instâncias disponíveis...")
try:
    response = requests.get(
        f"{BASE_URL}/instance/fetchInstances",
        headers=headers,
        timeout=10
    )
    print(f"✅ Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"📋 Instâncias encontradas: {len(data)}")
        for idx, inst in enumerate(data, 1):
            print(f"\n   {idx}. Nome: {inst.get('instance', {}).get('instanceName', 'N/A')}")
            print(f"      Estado: {inst.get('instance', {}).get('state', 'N/A')}")
            print(f"      Status: {inst.get('instance', {}).get('status', 'N/A')}")
    else:
        print(f"⚠️ Response: {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

# 3. Teste de envio (será preenchido quando tiver instância e número)
print("\n3️⃣ Verificando status da instância 'instanciateste'...")
try:
    response = requests.get(
        f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}",
        headers=headers,
        timeout=10
    )
    print(f"✅ Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"📱 Estado: {data}")
    else:
        print(f"⚠️ Response: {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n4️⃣ Testando envio de mensagem...")
TEST_NUMBER = "5542988463898"
try:
    payload = {
        "number": TEST_NUMBER,
        "text": "🚕 **Teste MinasTaxi Evolution API**\n\nMensagem de teste do sistema de automação.\n\nData: 30/12/2025"
    }
    
    response = requests.post(
        f"{BASE_URL}/message/sendText/{INSTANCE_NAME}",
        headers=headers,
        json=payload,
        timeout=15
    )
    
    print(f"✅ Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"📨 Mensagem enviada com sucesso!")
        print(f"📋 Response: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Erro no envio: {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "=" * 60)
print("Teste concluído!")
print("=" * 60)
