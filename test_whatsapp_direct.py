"""Teste direto da Evolution API"""
import requests
import json

url = "https://evolution-api-production-d234.up.railway.app/message/sendText/taxiautomacao"
headers = {
    "apikey": "minas2025taxi2026automacao",
    "Content-Type": "application/json"
}
payload = {
    "number": "5542988463898",
    "text": "🚖 Teste do sistema de táxi!\n\nSe você recebeu esta mensagem, o WhatsApp está FUNCIONANDO! ✅"
}

print("Enviando mensagem...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201]:
        print("\n✅ SUCESSO! Mensagem enviada!")
    else:
        print(f"\n❌ ERRO: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("\n⏱️ TIMEOUT - Servidor demorou mais de 60s para responder")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
