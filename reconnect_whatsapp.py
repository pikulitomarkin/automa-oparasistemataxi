"""
Reconecta instância WhatsApp Evolution API
"""
import requests
import json
import time

API_URL = "https://evolution-api-production-0290.up.railway.app"
API_KEY = "minas2025taxi2026automacao"
INSTANCE_NAME = "minastaxi2025"

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

print("\n" + "="*70)
print("🔄 RECONEXÃO - EVOLUTION API WHATSAPP")
print("="*70)

# PASSO 1: Desconectar (logout)
print("\n🔌 PASSO 1: Desconectando instância atual...")
try:
    url = f"{API_URL}/instance/logout/{INSTANCE_NAME}"
    print(f"DELETE {url}")
    response = requests.delete(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Instância desconectada!")
    else:
        print(f"⚠️ Response: {response.text}")
except Exception as e:
    print(f"⚠️ Erro: {e}")

print("\n⏳ Aguardando 3 segundos...")
time.sleep(3)

# PASSO 2: Reconectar e obter QR Code
print("\n📱 PASSO 2: Obtendo QR Code para reconexão...")
try:
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=15)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resposta recebida:")
        print(json.dumps(data, indent=2))
        
        # Procura por QR Code
        qr_code = None
        if 'qrcode' in data:
            qr_code = data['qrcode'].get('code') if isinstance(data['qrcode'], dict) else data['qrcode']
        elif 'code' in data:
            qr_code = data['code']
        elif 'base64' in data:
            qr_code = data['base64']
            
        if qr_code:
            print("\n" + "="*70)
            print("📱 QR CODE - ESCANEIE COM SEU WHATSAPP")
            print("="*70)
            print(f"\n{qr_code}\n")
            print("="*70)
            print("\n📋 COMO ESCANEAR:")
            print("1. Abra WhatsApp no celular")
            print("2. Vá em Menu (⋮) > Aparelhos conectados")
            print("3. Toque em 'Conectar um aparelho'")
            print("4. Aponte a câmera para o QR Code acima")
            print("="*70)
        else:
            print("\n⚠️ QR Code não encontrado na resposta")
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# PASSO 3: Verificar conexão
print("\n⏳ Aguardando 10 segundos para escanear QR Code...")
print("   (Escaneie o QR Code agora!)")
time.sleep(10)

print("\n🔍 PASSO 3: Verificando status da conexão...")
try:
    url = f"{API_URL}/instance/connectionState/{INSTANCE_NAME}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        state = data.get('instance', {}).get('state') or data.get('state')
        
        print(f"\n📊 Estado atual: {state}")
        
        if state == 'open':
            print("\n✅ ✅ ✅ SUCESSO! WHATSAPP CONECTADO! ✅ ✅ ✅")
            print("\n🎉 Agora você pode:")
            print("   • Executar: py test_whatsapp_direct.py")
            print("   • Enviar mensagens via sistema")
        else:
            print(f"\n⚠️ Estado: {state}")
            print("   Se não escaneou o QR Code, execute novamente este script")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*70)
