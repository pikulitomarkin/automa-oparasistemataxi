"""
Teste de envio para número 31999999926
"""
import requests
import json

BASE_URL = "https://evolution-api-production-98d2.up.railway.app"
API_KEY = "minas2025taxi2026automacao"
INSTANCE_NAME = "instanciateste"
TEST_NUMBER = "5531999999926"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 60)
print(f"TESTE DE ENVIO PARA {TEST_NUMBER}")
print("=" * 60)

payload = {
    "number": TEST_NUMBER,
    "text": "🚕 **MinasTaxi - Teste de Envio**\n\nOlá! Esta é uma mensagem de teste do sistema de automação de táxi.\n\n✅ Sistema operacional\n📱 WhatsApp integrado\n🗓️ 30/12/2025 - 23:40"
}

try:
    response = requests.post(
        f"{BASE_URL}/message/sendText/{INSTANCE_NAME}",
        headers=headers,
        json=payload,
        timeout=15
    )
    
    print(f"\n📊 Status HTTP: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"\n📋 Detalhes:")
        print(f"   • Remote JID: {data.get('key', {}).get('remoteJid')}")
        print(f"   • Message ID: {data.get('key', {}).get('id')}")
        print(f"   • Status: {data.get('status')}")
        print(f"   • Type: {data.get('messageType')}")
        print(f"\n📄 Response completa:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro no envio!")
        print(f"📄 Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro na requisição: {e}")

print("\n" + "=" * 60)
