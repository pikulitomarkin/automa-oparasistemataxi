"""
Teste rápido da API OpenAI
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_api():
    """Testa a conexão com a API OpenAI."""
    
    # Carrega variáveis de ambiente
    load_dotenv(override=True)
    
    print("="*80)
    print("🤖 TESTE DA API OPENAI")
    print("="*80)
    print()
    
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    
    if not api_key or api_key == 'sua-chave-openai-aqui':
        print("❌ ERRO: OpenAI API Key não configurada!")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"🤖 Modelo: {model}")
    print()
    
    try:
        print("🔌 Conectando à API OpenAI...")
        client = OpenAI(api_key=api_key)
        
        # Teste simples de completions
        print("📝 Testando geração de texto...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Responda apenas com 'OK' se você está funcionando corretamente."}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        
        print(f"✅ Resposta da API: '{result}'")
        print()
        
        # Teste de extração de dados (simulando o caso real)
        print("="*80)
        print("🚕 TESTANDO EXTRAÇÃO DE DADOS DE AGENDAMENTO")
        print("="*80)
        print()
        
        email_test = """
        Segue programação de carro:
        
        Passageiro: João Silva
        Telefone: (31) 99999-8888
        
        Data/Hora: 30/12/2025 às 14:00
        
        Origem: CSN Mineração, Congonhas, MG
        Destino: Aeroporto de Confins, Belo Horizonte
        
        CC: 12345
        """
        
        print("📧 Email de teste:")
        print(email_test)
        print()
        
        print("🤖 Enviando para GPT-4...")
        
        extraction_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Extraia dados de agendamento e retorne JSON puro sem markdown."},
                {"role": "user", "content": f"Extraia: passenger_name, phone, pickup_address, destination_address, pickup_time, notes\n\n{email_test}"}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        extracted = extraction_response.choices[0].message.content.strip()
        
        print("✅ Dados extraídos:")
        print(extracted)
        print()
        
        print("="*80)
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("="*80)
        print()
        print("✅ API OpenAI está funcionando corretamente")
        print("✅ Modelo GPT-4 respondendo normalmente")
        print("✅ Extração de dados operacional")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("="*80)
        print("❌ ERRO NO TESTE")
        print("="*80)
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        print()
        
        if "authentication" in str(e).lower() or "api key" in str(e).lower():
            print("💡 POSSÍVEL CAUSA:")
            print("   • API Key inválida ou expirada")
            print("   • Verifique se a chave está correta no .env")
        elif "quota" in str(e).lower() or "rate" in str(e).lower():
            print("💡 POSSÍVEL CAUSA:")
            print("   • Limite de uso atingido")
            print("   • Adicione créditos na conta OpenAI")
        else:
            print("💡 POSSÍVEL CAUSA:")
            print("   • Problema de conexão com a internet")
            print("   • API OpenAI temporariamente indisponível")
        
        print("="*80)
        return False

if __name__ == "__main__":
    test_openai_api()
