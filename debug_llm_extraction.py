"""
Debug: Verificar como o LLM está extraindo dados dos múltiplos passageiros
"""
import os
import sys
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.llm_extractor import LLMExtractor

def debug_extraction():
    """Debug detalhado da extração LLM"""
    
    email_body = """
    Assunto: Novo Agendamento
    
    Data: 30/12/2025
    Horário de chegada DELP: 08:00
    
    Passageiros:
    1. João Silva - (31) 98888-1111 - Rua das Flores, 100, Belo Horizonte, MG
    2. Maria Santos - (31) 98888-2222 - Avenida Paulista, 200, Belo Horizonte, MG
    3. Pedro Costa - (31) 98888-3333 - Rua Rio de Janeiro, 300, Belo Horizonte, MG
    
    Destino: DELP - Delegacia de Polícia
    Centro de custo: 1.07002.07.001
    """
    
    print("🔍 DEBUG: EXTRAÇÃO LLM")
    print("="*60)
    
    try:
        extractor = LLMExtractor(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4o')
        )
        
        extracted_data = extractor.extract_order_data(email_body)
        
        if not extracted_data:
            print("❌ Dados não extraídos")
            return
        
        print("✅ DADOS EXTRAÍDOS (JSON completo):")
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        
        print("\n" + "="*60)
        print("📊 ANÁLISE DETALHADA:")
        print("="*60)
        
        print(f"🔹 pickup_address: {extracted_data.get('pickup_address')}")
        print(f"🔹 dropoff_address: {extracted_data.get('dropoff_address')}")
        print(f"🔹 passenger_name: {extracted_data.get('passenger_name')}")
        print(f"🔹 phone: {extracted_data.get('phone')}")
        print(f"🔹 passengers (count): {len(extracted_data.get('passengers', []))}")
        
        print("\n📋 PASSAGEIROS INDIVIDUAIS:")
        for idx, passenger in enumerate(extracted_data.get('passengers', []), 1):
            print(f"  {idx}. Nome: {passenger.get('name')}")
            print(f"     Tel: {passenger.get('phone')}")
            print(f"     End: {passenger.get('address')}")
            print()
        
        print("🤔 PROBLEMA IDENTIFICADO:")
        if extracted_data.get('pickup_address') and len(extracted_data.get('passengers', [])) > 1:
            first_passenger_addr = extracted_data.get('passengers', [{}])[0].get('address', '')
            if extracted_data.get('pickup_address') == first_passenger_addr:
                print("❌ pickup_address = endereço do primeiro passageiro apenas")
                print("   Deveria considerar múltiplos pontos de coleta ou lógica específica")
            else:
                print("✅ pickup_address diferente dos endereços individuais")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction()