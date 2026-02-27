"""
Teste para verificar se o payment_type está sendo lido corretamente da variável de ambiente
"""
import os
import sys
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

print("\n" + "="*70)
print("VERIFICAÇÃO: Variável de Forma de Pagamento")
print("="*70)

# Verifica se a variável existe
payment_type_env = os.getenv('MINASTAXI_PAYMENT_TYPE')

print(f"\n1. Variável de ambiente MINASTAXI_PAYMENT_TYPE:")
if payment_type_env:
    print(f"   ✅ ENCONTRADA: '{payment_type_env}'")
else:
    print(f"   ⚠️  NÃO ENCONTRADA (usando default: 'ONLINE_PAYMENT')")

# Simula inicialização do MinasTaxiClient
print(f"\n2. Inicialização do MinasTaxiClient:")

# Adiciona o path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.minastaxi_client import MinasTaxiClient

# Inicializa com as mesmas configurações do processor.py
client = MinasTaxiClient(
    api_url=os.getenv('MINASTAXI_API_URL', 'https://vm2c.taxifone.com.br:11048'),
    user_id=os.getenv('MINASTAXI_USER_ID'),
    password=os.getenv('MINASTAXI_PASSWORD'),
    auth_header=os.getenv('MINASTAXI_AUTH_HEADER', 'Basic Original'),
    payment_type=os.getenv('MINASTAXI_PAYMENT_TYPE', 'ONLINE_PAYMENT'),
    timeout=int(os.getenv('MINASTAXI_TIMEOUT', 30)),
    max_retries=int(os.getenv('MINASTAXI_RETRY_ATTEMPTS', 3))
)

print(f"   Valor usado: '{os.getenv('MINASTAXI_PAYMENT_TYPE', 'ONLINE_PAYMENT')}'")
print(f"   Valor no client: '{client.payment_type}'")

if client.payment_type == payment_type_env:
    print(f"   ✅ CORRETO: payment_type do client corresponde ao .env")
elif not payment_type_env:
    print(f"   ⚠️  Usando valor default porque .env não tem a variável")
else:
    print(f"   ❌ ERRO: payment_type do client ('{client.payment_type}') != .env ('{payment_type_env}')")

# Verifica o payload
print(f"\n3. Verificação no payload de dispatch:")
print(f"   Quando dispatch_order() for chamado, o payload terá:")
print(f"   \"payment_type\": \"{client.payment_type}\"")

# Dicas
print("\n" + "="*70)
print("CONFIGURAÇÃO NO RAILWAY:")
print("="*70)
print("\n1. Acesse: https://railway.app (projeto taxi)")
print("2. Vá em 'Variables' ou 'Settings'")
print("3. Verifique se existe: MINASTAXI_PAYMENT_TYPE")
print("4. Valores possíveis:")
print("   - BE (Boleto Eletrônico)")
print("   - ONLINE_PAYMENT (Pagamento Online)")
print("   - BOLETO")
print("   - VOUCHER")
print("   - Outro valor específico da API")

print("\n5. IMPORTANTE: Após alterar no Railway, faça:")
print("   railway up --service taxi-automation")
print("   (ou espere o deploy automático)")

print("\n" + "="*70 + "\n")
