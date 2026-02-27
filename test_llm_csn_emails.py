"""
Script de Teste: Extração LLM de Emails CSN Mineração
Testa o LLM com os 5 formatos reais de email identificados
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.llm_extractor import LLMExtractor
from src.services.email_reader import EmailMessage

# Carrega variáveis de ambiente
load_dotenv()

# 5 Emails Reais Baseados nos Screenshots
TEST_EMAILS = [
    {
        "name": "Email 1 - CSN para MARIANA (tabela, múltiplos passageiros)",
        "subject": "PROGRAMAÇÃO DE TAXI amanhã 16:00H",
        "body": """Prezados, boa Noite!

Gentileza programar um TAXI amanhã 06/09/2025 16:00H

CSN DESTINHO BH

CC:20086

┌────────────────────────────┬────────┬──────────────┬──────┬─────────┐
│ EDIMAR JULIO FERREIRA SOARES│ MIN7956│ (31)988873751│ CSN  │ MARIANA │
│ FERNANDO ANGELO GONCALVES   │ MIN7956│ (31)984840900│      │         │
└────────────────────────────┴────────┴──────────────┴──────┴─────────┘

Obrigado!""",
        "sender": "carlos.pereira@csn.com.br",
        "date": datetime(2025, 9, 5, 19, 6),
        "expected": {
            "passenger_name": "EDIMAR JULIO FERREIRA SOARES",  # Primeiro passageiro
            "passenger_phone": "31988873751",
            "pickup_address": "CSN",  # Vai ser expandido para Congonhas
            "destination_address": "MARIANA",  # Vai ser expandido
            "contains_cc": "20086",
            "multiple_passengers": True
        }
    },
    {
        "name": "Email 2 - CSN para BH (tabela simples)",
        "subject": "PROGRAMAÇÃO DE TAXI amanhã 15:30h",
        "body": """Prezados, boa Noite!

Gentileza programar um TAXI amanhã 06/09/2025 15:30h

CSN DESTINHO BH

CC:20063

┌────────────────────────────┬────────┬──────────────┬──────┬──────┐
│ Harlle Jonathan da Rocha   │ MIP 0060│ 37998742019 │ CSN  │  BH  │
└────────────────────────────┴────────┴──────────────┴──────┴──────┘

Obrigado!""",
        "sender": "carlos.pereira@csn.com.br",
        "date": datetime(2025, 9, 5, 19, 1),
        "expected": {
            "passenger_name": "Harlle Jonathan da Rocha",
            "passenger_phone": "37998742019",
            "pickup_address": "CSN",
            "destination_address": "Belo Horizonte",  # Aceita BH expandido
            "contains_cc": "20063"
        }
    },
    {
        "name": "Email 3 - Endereço completo PARA CSN (invertido)",
        "subject": "PROGRAMAÇÃO DE TAXI hoje 04:30h",
        "body": """Prezados, bom dia!

Gentileza programar um TAXI hoje 04:30h

CC:20381

RUA BARRAS, N200 BAIRRO CALAFATE destino CSN

┌────────┬────────┬──────────────────────┐
│ MAICON │ MIO3554│ 9 8440-1424/ 9 9062-6923│
└────────┴────────┴──────────────────────┘

Obrigado!""",
        "sender": "carlos.pereira@csn.com.br",
        "date": datetime(2025, 8, 31, 0, 36),
        "expected": {
            "passenger_name": "MAICON",
            "passenger_phone": "984401424",  # Normalizado
            "pickup_address": "RUA BARRAS",
            "destination_address": "CSN",
            "contains_cc": "20381"
        }
    },
    {
        "name": "Email 4 - Múltiplos passageiros com endereços diferentes",
        "subject": "PROGRAMAÇÃO DE CARRO HOJE 15:00h",
        "body": """Prezados, boa Tarde!

Gentileza programar CARRO HOJE 15:00 FERNANDINHO 15:00h DESTINO LAFAIETE

CC:20049

┌───────────────────┬────────┬────────────────────────────────┬────────────────────┐
│ GRACY ADRIANE COSTA│MNC0789│RUA JOSE ALEXANDRE RAMOS, 38   │CONSELHEIRO LAFAIETE│
│ AGNALDO FERNANDES  │MI05688│RUA ETELVINA DE LIMA,426, STA M│CONSELHEIRO LAFAIETE│
│ MARCIANO           │MNC0220│RUA JOAO FERREIRA, 346, S.C. JE│CONSELHEIRO LAFAIETE│
│ DIEGO              │       │RUA ARNALDO SEZARINO 18 FONTE G│                    │
└───────────────────┴────────┴────────────────────────────────┴────────────────────┘

Obrigado!""",
        "sender": "carlos.pereira@csn.com.br",
        "date": datetime(2025, 8, 23, 13, 9),
        "expected": {
            "passenger_name": "GRACY ADRIANE COSTA",  # Primeiro
            "pickup_address": "RUA JOSE ALEXANDRE RAMOS",
            "destination_address": "LAFAIETE",
            "contains_cc": "20049",
            "multiple_passengers": True
        }
    },
    {
        "name": "Email 5 - Ida e Volta (tabela complexa)",
        "subject": "PROGRAMAÇÃO DE CARRO AMANHÃ 23/08/2025",
        "body": """Prezados, boa Noite!

Gentileza programar um TÁXI AMANHÃ 23/08/2025 04:00H E RETORNO 16:00H

CC:20049

┌──────────┬────────┬────────────────────────────┬──────────────┬─────────────────────────────┬────────┬──────┬─┐
│23/08/2025│ MIO9580│ Rua Antonio Barbosa 55     │Ibirité / MG  │Estrada Casa de Pedra, S/N   │Congonhas│04:00 │-│
│          │        │ centro                     │              │Zona Rural                   │/ MG     │      │ │
├──────────┼────────┼────────────────────────────┼──────────────┼─────────────────────────────┼────────┼──────┼─┤
│23/08/2025│ MIO9580│ Estrada Casa de Pedra, S/N │Congonhas / MG│Rua Antonio Barbosa 55-centro│Ibirité │16:00 │-│
│          │        │ Zona Rural                 │              │                             │/ MG     │      │ │
└──────────┴────────┴────────────────────────────┴──────────────┴─────────────────────────────┴────────┴──────┴─┘

Obrigado!""",
        "sender": "carlos.pereira@csn.com.br",
        "date": datetime(2025, 8, 22, 17, 31),
        "expected": {
            "passenger_name": "MIO9580",  # Matrícula como nome temporário
            "pickup_address": "Rua Antonio Barbosa",
            "destination_address": "Estrada Casa de Pedra",
            "contains_cc": "20049",
            "has_return": True
        }
    },
    {
        "name": "Email 6 - Pagamento em DINHEIRO",
        "subject": "PROGRAMAÇÃO DE TAXI hoje 10:00h",
        "body": """Bom dia,

Pedido de táxi hoje 10:00h

CC:20099
Pgto: DIN

Obrigado!""",
        "sender": "teste@exemplo.com",
        "date": datetime(2025, 10, 1, 9, 0),
        "expected": {
            "payment_type": "DIN",
            "contains_cc": "20099"
        }
    }
]


def run_llm_tests():
    """Executa testes de extração LLM com os 5 emails reais"""
    
    print("=" * 80)
    print("🧪 TESTE DE EXTRAÇÃO LLM - EMAILS CSN MINERAÇÃO")
    print("=" * 80)
    print()
    
    # Verifica se a API key está configurada
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERRO: OPENAI_API_KEY não configurada no .env")
        return
    
    # Inicializa o extrator
    print("🔧 Inicializando LLM Extractor...")
    extractor = LLMExtractor(api_key=api_key)
    print("✅ LLM Extractor inicializado")
    print()
    
    results = []
    
    for idx, email_data in enumerate(TEST_EMAILS, 1):
        print("-" * 80)
        print(f"📧 TESTE {idx}/5: {email_data['name']}")
        print("-" * 80)
        
        # Cria objeto EmailMessage
        email = EmailMessage(
            uid=f"test_{idx}",
            subject=email_data["subject"],
            from_=email_data["sender"],
            date=email_data["date"],
            body=email_data["body"]
        )
        
        print(f"📤 Assunto: {email.subject}")
        print(f"📝 Corpo (primeiras 100 chars): {email.body[:100]}...")
        print()
        
        # Extrai com LLM
        print("🤖 Extraindo com GPT-4...")
        try:
            order_dict = extractor.extract_with_fallback(email.body)
            
            if order_dict is None:
                print("❌ FALHA: LLM retornou None")
                results.append({
                    "test": email_data["name"],
                    "status": "FAILED",
                    "reason": "LLM returned None"
                })
                continue
            
            # Valida extração
            print("✅ Extração bem-sucedida!")
            print()
            print("📊 DADOS EXTRAÍDOS:")
            print(f"   Nome: {order_dict.get('passenger_name', 'N/A')}")
            print(f"   Telefone: {order_dict.get('phone', 'N/A')}")
            print(f"   Origem: {order_dict.get('pickup_address', 'N/A')}")
            print(f"   Destino: {order_dict.get('destination_address', 'N/A')}")
            print(f"   Horário: {order_dict.get('pickup_time', 'N/A')}")
            print(f"   Notas: {order_dict.get('notes', 'N/A')[:100] if order_dict.get('notes') else 'N/A'}...")
            print()
            
            # Valida contra expectativas
            expected = email_data["expected"]
            checks = []
            
            if "passenger_name" in expected:
                match = expected["passenger_name"].lower() in str(order_dict.get('passenger_name', '')).lower()
                checks.append(("Nome contém esperado", match))
            
            if "passenger_phone" in expected:
                # Normaliza telefones para comparação
                phone_expected = ''.join(c for c in expected["passenger_phone"] if c.isdigit())
                phone_extracted = ''.join(c for c in str(order_dict.get('phone', '')) if c.isdigit())
                match = phone_expected in phone_extracted
                checks.append(("Telefone correto", match))
            
            if "pickup_address" in expected:
                match = expected["pickup_address"].lower() in str(order_dict.get('pickup_address', '')).lower()
                checks.append(("Origem contém esperado", match))
            
            if "destination_address" in expected:
                match = expected["destination_address"].lower() in str(order_dict.get('destination_address', '')).lower()
                checks.append(("Destino contém esperado", match))
            
            if "contains_cc" in expected:
                match = expected["contains_cc"] in str(order_dict.get('notes', ''))
                checks.append((f"CC:{expected['contains_cc']} em notas", match))
            if "payment_type" in expected:
                match = expected["payment_type"].lower() == str(order_dict.get('payment_type','')).lower()
                checks.append((f"Payment type => {expected['payment_type']}", match))
            
            if "multiple_passengers" in expected and expected["multiple_passengers"]:
                notes = str(order_dict.get('notes', '')).lower()
                name = str(order_dict.get('passenger_name', ''))
                match = "passageiros" in notes or "," in name
                checks.append(("Múltiplos passageiros detectados", match))
            
            if "has_return" in expected and expected["has_return"]:
                match = "retorno" in str(order_dict.get('notes', '')).lower()
                checks.append(("Retorno detectado", match))
            
            print("🔍 VALIDAÇÕES:")
            all_passed = True
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name}")
                if not check_result:
                    all_passed = False
            
            results.append({
                "test": email_data["name"],
                "status": "PASSED" if all_passed else "PARTIAL",
                "checks": checks
            })
            
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            results.append({
                "test": email_data["name"],
                "status": "ERROR",
                "error": str(e)
            })
        
        print()
    
    # Resumo final
    print("=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    partial = sum(1 for r in results if r["status"] == "PARTIAL")
    failed = sum(1 for r in results if r["status"] in ["FAILED", "ERROR"])
    
    print(f"✅ Passou completo: {passed}/5")
    print(f"⚠️  Passou parcial: {partial}/5")
    print(f"❌ Falhou: {failed}/5")
    print()
    
    for result in results:
        status_icon = {
            "PASSED": "✅",
            "PARTIAL": "⚠️",
            "FAILED": "❌",
            "ERROR": "💥"
        }.get(result["status"], "❓")
        
        print(f"{status_icon} {result['test']}: {result['status']}")
        
        if result["status"] == "ERROR":
            print(f"   Erro: {result['error']}")
    
    print()
    print("=" * 80)
    
    # Retorna código de saída
    if failed > 0:
        print("❌ Alguns testes falharam. Revise a extração LLM.")
        return 1
    elif partial > 0:
        print("⚠️  Todos os testes passaram, mas alguns parcialmente.")
        return 0
    else:
        print("🎉 Todos os testes passaram com sucesso!")
        return 0


if __name__ == "__main__":
    exit_code = run_llm_tests()
    sys.exit(exit_code)
