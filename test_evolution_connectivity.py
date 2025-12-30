"""
Testa conectividade básica com Evolution API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv('EVOLUTION_API_URL')
api_key = os.getenv('EVOLUTION_API_KEY')

print("\n🔍 TESTE DE CONECTIVIDADE - EVOLUTION API\n")
print(f"📡 URL Base: {api_url}")
print("-" * 60)

# Remove trailing slash
base_url = api_url.rstrip('/')

# Lista de endpoints para testar
endpoints = [
    "/",
    "/instance/fetchInstances",
    "/instance/connect/taxiautomacao",
    "/message/sendText/taxiautomacao",
]

headers = {
    'apikey': api_key,
    'Content-Type': 'application/json'
}

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    print(f"\n🔄 Testando: {endpoint}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 404:
            print(f"   ✅ Endpoint existe!")
            try:
                data = response.json()
                print(f"   Response: {str(data)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Endpoint não encontrado (404)")
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "="*60)
print("📋 DIAGNÓSTICO:")
print("="*60)
print("\n⚠️ A Evolution API pode estar:")
print("   1. Offline ou não acessível")
print("   2. Em uma versão diferente (endpoints mudaram)")
print("   3. Requer autenticação diferente")
print("\n💡 AÇÕES RECOMENDADAS:")
print("   1. Verifique se o Railway da Evolution API está rodando")
print("   2. Acesse o dashboard diretamente no navegador:")
print(f"      {api_url}")
print("   3. Consulte a documentação da Evolution API v2")
print("   4. Verifique se a API Key está correta")
