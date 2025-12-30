"""
Teste do novo formato CSN - Múltiplos passageiros + Ida e Volta
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from src.services.llm_extractor import LLMExtractor

# Email de exemplo fornecido pelo usuário
EMAIL_BODY = """
Data: 29/12/2025			
			
Horário de chegada DELP: 05H40			
Horário de retorno DELP: 13H40			
			
Endereço	Ellen Santos Souza	Rua Piuai , n 1056 bairro Celvia - Vespasiano 	Celular	 99379-0517	CENTRO DE CUSTO1.07002.07.001
Endereço	Soraria Alves Gualberto	Rua Maria Ana da Silva, n 77( antiga rua do capim) bairro Názea	Celular	98496-4897	CENTRO DE CUSTO 1.07002.07.001
Endereço	Maria Carolina Rocha	Avenida B, n 420 Vila Esportiva Vespasiano	Celular	99622-2573	CENTRO DE CUSTO 1.07002.07.001
Endereço	Naiara Alves Gomes	Rua Joaquim de Castro, n 150 bairro Minas Caixa - Belo Horizonte	991378714	CENTRO DE CUSTO 1.07002.07.001
"""

def test_new_format():
    """Testa extração do novo formato com múltiplos passageiros"""
    
    print("=" * 80)
    print("🧪 TESTE: NOVO FORMATO CSN - MÚLTIPLOS PASSAGEIROS + IDA/VOLTA")
    print("=" * 80)
    print()
    
    print("📧 EMAIL DE ENTRADA:")
    print("-" * 80)
    print(EMAIL_BODY)
    print("-" * 80)
    print()
    
    # Inicializa extractor
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o')
    
    if not api_key or 'sua-chave' in api_key:
        print("❌ OpenAI API Key não configurada!")
        return
    
    print(f"🤖 Inicializando LLM Extractor...")
    print(f"   Modelo: {model}")
    print()
    
    extractor = LLMExtractor(api_key=api_key, model=model)
    
    # Extrai dados
    print("🔄 Extraindo dados...")
    print()
    
    try:
        result = extractor.extract_with_fallback(EMAIL_BODY, max_retries=2)
        
        if not result:
            print("❌ Falha na extração!")
            return
        
        print("✅ DADOS EXTRAÍDOS:")
        print("=" * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=" * 80)
        print()
        
        # Validações
        print("🔍 VALIDAÇÕES:")
        print("-" * 80)
        
        # Passageiros
        passengers = result.get('passengers', [])
        print(f"✅ Passageiros extraídos: {len(passengers)}")
        for idx, p in enumerate(passengers, 1):
            print(f"   {idx}. {p.get('name')} - {p.get('phone')}")
            print(f"      {p.get('address')}")
        print()
        
        # Horários
        has_return = result.get('has_return', False)
        arrival_time = result.get('arrival_time')
        return_time = result.get('return_time')
        pickup_time = result.get('pickup_time')
        
        print(f"{'✅' if has_return else '❌'} Tem retorno: {has_return}")
        print(f"⏰ Horário de chegada: {arrival_time or 'N/A'}")
        print(f"⏰ Horário de retorno: {return_time or 'N/A'}")
        print(f"⏰ Horário de saída: {pickup_time or 'N/A (será calculado)'}")
        print()
        
        # Destino
        destination = result.get('dropoff_address', 'N/A')
        print(f"🎯 Destino: {destination}")
        print()
        
        # Centro de custo
        notes = result.get('notes', '')
        if 'CENTRO DE CUSTO' in notes or 'CC' in notes:
            print(f"💰 Centro de Custo encontrado em notes")
        print()
        
        print("=" * 80)
        print("🎯 PRÓXIMOS PASSOS:")
        print("=" * 80)
        print("1. ✅ LLM extrai múltiplos passageiros")
        print("2. 🔄 Criar lógica para calcular horário de saída (chegada - tempo)")
        print("3. 🔄 Criar 2 orders: IDA e VOLTA")
        print("4. 🔄 Enviar para MinasTaxi com array de passageiros")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}")
        print(f"   {str(e)}")

if __name__ == "__main__":
    test_new_format()
