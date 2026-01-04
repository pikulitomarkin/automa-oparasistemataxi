"""
Teste de extração de código da empresa do email
"""
from src.services.llm_extractor import LLMExtractor
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Email de teste do cliente
test_email = """*Empresa: 284 - Delp Engenharia*
Fone: 31 999999926
Nome: Gasparino Rodrigues da Silva
Origem: RUA Jorge Dias de Oliva, 172, Vespasiano, MG
Destino: Delp Engenharia Vespasiano (Av. das Nações, 999 - Distrito Industrial, Vespasiano - MG, 33201-003)
Centro de Custo: 1.07002.07.004
*Agendamento: 21/01/26*
Horário de Chegada: 05:45 hs"""

print("=" * 60)
print("🧪 TESTE DE EXTRAÇÃO DE CÓDIGO DA EMPRESA")
print("=" * 60)
print("\n📧 Email de Teste:")
print(test_email)
print("\n" + "-" * 60)

# Extrai dados com LLM
extractor = LLMExtractor(api_key=os.getenv('OPENAI_API_KEY'))
data = extractor.extract_with_fallback(test_email)

if data:
    print("\n✅ Dados Extraídos:")
    print(f"  👤 Nome: {data.get('passenger_name')}")
    print(f"  📞 Telefone: {data.get('phone')}")
    print(f"  📍 Origem: {data.get('pickup_address')}")
    print(f"  🎯 Destino: {data.get('dropoff_address')}")
    print(f"  🕐 Horário: {data.get('pickup_time')}")
    print(f"  💰 Centro de Custo: {data.get('notes')}")
    print(f"  🏢 Código da Empresa: {data.get('company_code')}")
    
    print("\n" + "=" * 60)
    
    # Validações
    company_code = data.get('company_code')
    if company_code == "284":
        print("✅ Código da empresa extraído corretamente: 284")
    else:
        print(f"❌ Código incorreto: esperado '284', obtido '{company_code}'")
    
    if "1.07002.07.004" in (data.get('notes') or ""):
        print("✅ Centro de custo presente nas notas: 1.07002.07.004")
    else:
        print("❌ Centro de custo não encontrado nas notas")
        
else:
    print("❌ Falha na extração dos dados")

print("=" * 60)
