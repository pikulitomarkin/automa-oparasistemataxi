"""
Teste direto da Evolution API - SEM CACHE
"""
import requests
import json

# CREDENCIAIS DIRETAS (atualizadas)
API_URL = "https://evolution-api-production-0290.up.railway.app"
API_KEY = "minas2025taxi2026automacao"
INSTANCE_NAME = "minastaxi2025"

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

print("\n" + "="*70)
print("🔧 TESTE DIRETO - EVOLUTION API")
print("="*70)
print(f"\n📡 URL: {API_URL}")
print(f"🔑 Instance: {INSTANCE_NAME}")

# ============================================================================
# PASSO 1: Listar instâncias
# ============================================================================
print("\n" + "-"*70)
print("🔍 PASSO 1: Listando instâncias disponíveis...")
print("-"*70)

try:
    url = f"{API_URL}/instance/fetchInstances"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
except Exception as e:
    print(f"❌ Erro: {e}")

# ============================================================================
# PASSO 2: Status da conexão específica
# ============================================================================
print("\n" + "-"*70)
print(f"🔍 PASSO 2: Verificando instância '{INSTANCE_NAME}'...")
print("-"*70)

try:
    url = f"{API_URL}/instance/connectionState/{INSTANCE_NAME}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Instância encontrada!")
        print(json.dumps(data, indent=2))
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# ============================================================================
# PASSO 3: Conectar e obter QR Code
# ============================================================================
print("\n" + "-"*70)
print("🔍 PASSO 3: Tentando obter QR Code...")
print("-"*70)

try:
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=15)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Resposta recebida:")
        print(json.dumps(data, indent=2))
        
        # Tenta extrair QR Code
        if 'qrcode' in data or 'code' in data or 'base64' in str(data):
            print("\n" + "="*70)
            print("📱 QR CODE DISPONÍVEL - Escaneie com WhatsApp!")
            print("="*70)
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# ============================================================================
# RESUMO
# ============================================================================
print("\n" + "="*70)
print("📋 DIAGNÓSTICO:")
print("="*70)
print("""
Se todos os endpoints retornaram 404:
  ❌ A Evolution API pode não estar rodando corretamente
  ❌ A URL pode estar incorreta
  ❌ Verifique o Railway Dashboard da Evolution API

Se a instância não foi encontrada:
  ⚠️ Você precisa criar a instância primeiro
  → Acesse: https://evolution-api-production-1a45.up.railway.app
  → Crie instância: minastaxi2025

Se o QR Code apareceu:
  ✅ Escaneie com WhatsApp
  ✅ Aguarde 10-15 segundos
  ✅ Execute: py test_whatsapp_direct.py
""")
