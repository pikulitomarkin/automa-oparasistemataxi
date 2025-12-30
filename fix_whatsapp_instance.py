"""
Script completo para diagnosticar e reconectar instância WhatsApp Evolution API
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv('EVOLUTION_API_URL', 'https://evolution-api-production-1a45.up.railway.app').rstrip('/')
API_KEY = os.getenv('EVOLUTION_API_KEY', 'minas2025taxi2026automacao')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME', 'minastaxi2025')

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

print("\n" + "="*70)
print("🔧 DIAGNÓSTICO E RECONEXÃO - EVOLUTION API WHATSAPP")
print("="*70)
print(f"\n📡 URL: {API_URL}")
print(f"🔑 Instance: {INSTANCE_NAME}")
print(f"🔐 API Key: {API_KEY[:10]}...")

# ============================================================================
# PASSO 1: Verificar se a instância existe
# ============================================================================
print("\n" + "-"*70)
print("🔍 PASSO 1: Verificando se a instância existe...")
print("-"*70)

try:
    url = f"{API_URL}/instance/fetchInstances"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        instances = response.json()
        print(f"✅ API respondeu! Instâncias encontradas: {len(instances) if isinstance(instances, list) else 1}")
        
        # Procura pela instância específica
        instance_found = False
        for inst in (instances if isinstance(instances, list) else [instances]):
            if isinstance(inst, dict):
                inst_name = inst.get('instance', {}).get('instanceName') or inst.get('instanceName')
                if inst_name == INSTANCE_NAME:
                    instance_found = True
                    state = inst.get('instance', {}).get('state') or inst.get('state')
                    print(f"\n✅ Instância '{INSTANCE_NAME}' encontrada!")
                    print(f"   Status: {state}")
                    break
        
        if not instance_found:
            print(f"\n❌ Instância '{INSTANCE_NAME}' NÃO foi encontrada!")
            print("\n💡 Você precisa criar a instância primeiro.")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro ao verificar instâncias: {e}")

# ============================================================================
# PASSO 2: Verificar status de conexão
# ============================================================================
print("\n" + "-"*70)
print("🔍 PASSO 2: Verificando status da conexão...")
print("-"*70)

try:
    url = f"{API_URL}/instance/connectionState/{INSTANCE_NAME}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resposta: {json.dumps(data, indent=2)}")
        
        state = data.get('instance', {}).get('state') or data.get('state')
        if state == 'open':
            print(f"\n✅ INSTÂNCIA CONECTADA! Estado: {state}")
        else:
            print(f"\n⚠️ INSTÂNCIA DESCONECTADA! Estado: {state}")
            print("   Você precisa escanear o QR Code novamente.")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro ao verificar conexão: {e}")

# ============================================================================
# PASSO 3: Obter QR Code (se desconectado)
# ============================================================================
print("\n" + "-"*70)
print("🔍 PASSO 3: Gerando QR Code (se necessário)...")
print("-"*70)

try:
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=15)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'qrcode' in data or 'code' in data:
            qrcode = data.get('qrcode') or data.get('code')
            print(f"\n📱 QR CODE DISPONÍVEL!")
            print(f"\n{qrcode.get('code') if isinstance(qrcode, dict) else qrcode}")
            print("\n" + "="*70)
            print("👆 ESCANEIE ESTE QR CODE COM SEU WHATSAPP:")
            print("="*70)
            print("1. Abra WhatsApp no celular")
            print("2. Vá em Menu (⋮) > Aparelhos conectados")
            print("3. Toque em 'Conectar um aparelho'")
            print("4. Aponte a câmera para o QR Code acima")
            print("="*70)
        else:
            print(f"✅ Resposta: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro ao obter QR Code: {e}")

# ============================================================================
# PASSO 4: Teste de envio (opcional)
# ============================================================================
print("\n" + "-"*70)
print("📋 PRÓXIMOS PASSOS:")
print("-"*70)
print("""
1. Se aparecer QR Code acima:
   - Escaneie com seu WhatsApp
   - Aguarde 10-15 segundos
   - Execute novamente: py test_whatsapp_direct.py

2. Se a instância não foi encontrada:
   - Acesse o Railway Dashboard da Evolution API
   - Crie uma instância chamada: minastaxi2025
   - Execute este script novamente

3. Se já está conectado:
   - Execute: py test_whatsapp_direct.py
   - Envie mensagem de teste

4. Verificar logs do Railway:
   - Os erros "keep alive" devem parar após conexão
   - Se continuar, restart o serviço Evolution API no Railway
""")

print("\n" + "="*70)
print("🔄 DIAGNÓSTICO CONCLUÍDO!")
print("="*70)
