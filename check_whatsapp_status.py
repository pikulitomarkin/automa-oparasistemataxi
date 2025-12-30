"""
Verifica o status da instância Evolution API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv('EVOLUTION_API_URL')
api_key = os.getenv('EVOLUTION_API_KEY')
instance_name = os.getenv('EVOLUTION_INSTANCE_NAME')

print("\n🔍 VERIFICANDO STATUS DA INSTÂNCIA WHATSAPP\n")
print(f"📡 URL: {api_url}")
print(f"🔑 Instance: {instance_name}")
print("-" * 60)

# Endpoint para buscar instância
url = f"{api_url}/instance/fetchInstances"

headers = {
    'apikey': api_key,
    'Content-Type': 'application/json'
}

try:
    print("\n🔄 Buscando informações da instância...")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resposta recebida!")
        print(f"\n{'-'*60}")
        print(f"Dados completos:\n{data}")
        print(f"{'-'*60}")
        
        # Procura pela instância específica
        instances = data if isinstance(data, list) else [data]
        
        found = False
        for inst in instances:
            if isinstance(inst, dict) and inst.get('instance', {}).get('instanceName') == instance_name:
                found = True
                print(f"\n🎯 Instância encontrada: {instance_name}")
                print(f"   📱 Status: {inst.get('instance', {}).get('state', 'N/A')}")
                print(f"   🔌 Conectado: {inst.get('instance', {}).get('status', 'N/A')}")
                break
        
        if not found:
            print(f"\n⚠️ Instância '{instance_name}' não encontrada na lista!")
            print("\n💡 Você precisa:")
            print("   1. Criar a instância via Evolution API Dashboard")
            print("   2. Escanear o QR Code para conectar")
    else:
        print(f"\n❌ Erro na API: {response.status_code}")
        print(f"   Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"\n❌ Erro de conexão: {e}")
    print("\n🔧 Verifique:")
    print("   1. Se a Evolution API está online")
    print(f"   2. Se a URL está correta: {api_url}")
    print("   3. Se a API Key está correta")

print("\n" + "="*60)
print("📋 PRÓXIMOS PASSOS:")
print("="*60)
print("\n1. Se a instância não existe:")
print("   - Acesse o dashboard da Evolution API")
print(f"   - URL: {api_url}")
print(f"   - Crie uma instância chamada: {instance_name}")
print("   - Escaneie o QR Code com seu WhatsApp")
print("\n2. Se a instância existe mas está desconectada:")
print("   - Reconecte a instância no dashboard")
print("   - Pode ser necessário escanear o QR Code novamente")
print("\n3. Se a instância está conectada mas ainda dá erro:")
print("   - Verifique se a API Key está correta")
print("   - Tente reiniciar a instância")
