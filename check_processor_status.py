#!/usr/bin/env python
"""
Script para verificar se o processador contínuo está funcionando corretamente.
Útil para debug e monitoramento.
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def check_environment():
    """Verifica variáveis de ambiente necessárias."""
    print("=" * 60)
    print("VERIFICAÇÃO DE CONFIGURAÇÃO DO PROCESSADOR")
    print("=" * 60)
    
    required_vars = [
        'EMAIL_HOST',
        'EMAIL_USER',
        'EMAIL_PASSWORD',
        'OPENAI_API_KEY',
        'MINASTAXI_USER_ID',
        'MINASTAXI_PASSWORD'
    ]
    
    optional_vars = [
        'PROCESSOR_INTERVAL_MINUTES',
        'EMAIL_DAYS_BACK',
        'ENABLE_WHATSAPP_NOTIFICATIONS'
    ]
    
    print("\n✓ Variáveis Obrigatórias:")
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Oculta senhas/chaves
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✓ {var}: {display_value}")
        else:
            print(f"  ✗ {var}: NÃO CONFIGURADA")
            all_ok = False
    
    print("\n⚙️  Variáveis Opcionais:")
    for var in optional_vars:
        value = os.getenv(var, "não configurada")
        if value == "não configurada":
            # Valores padrão
            if var == 'PROCESSOR_INTERVAL_MINUTES':
                value = "15 (padrão)"
            elif var == 'EMAIL_DAYS_BACK':
                value = "7 (padrão)"
            elif var == 'ENABLE_WHATSAPP_NOTIFICATIONS':
                value = "false (padrão)"
        print(f"  • {var}: {value}")
    
    return all_ok


def check_database():
    """Verifica se o banco de dados existe e tem dados."""
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    
    db_path = os.getenv('DATABASE_PATH', 'data/taxi_orders.db')
    
    if not os.path.exists(db_path):
        print(f"  ✗ Banco de dados não encontrado: {db_path}")
        return False
    
    print(f"  ✓ Banco de dados encontrado: {db_path}")
    
    # Tenta conectar e obter estatísticas
    try:
        from src.services.database import DatabaseManager
        db = DatabaseManager(db_path)
        stats = db.get_statistics()
        
        print(f"\n  📊 Estatísticas:")
        print(f"    • Total de pedidos: {stats.get('total', 0)}")
        print(f"    • Despachados: {stats.get('dispatched', 0)}")
        print(f"    • Falhas: {stats.get('failed', 0)}")
        print(f"    • Revisão manual: {stats.get('manual_review', 0)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Erro ao acessar banco: {e}")
        return False


def check_logs():
    """Verifica arquivos de log."""
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DE LOGS")
    print("=" * 60)
    
    log_file = os.getenv('LOG_FILE', 'data/taxi_automation.log')
    
    if not os.path.exists(log_file):
        print(f"  ⚠️  Arquivo de log não encontrado: {log_file}")
        print(f"  (Será criado na primeira execução)")
        return True
    
    print(f"  ✓ Arquivo de log encontrado: {log_file}")
    
    # Lê últimas linhas
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print("  ⚠️  Arquivo de log está vazio")
            return True
        
        print(f"\n  📄 Últimas 10 linhas do log:")
        for line in lines[-10:]:
            print(f"    {line.rstrip()}")
        
        return True
    except Exception as e:
        print(f"  ✗ Erro ao ler log: {e}")
        return False


def check_processor_config():
    """Verifica configuração específica do processador."""
    print("\n" + "=" * 60)
    print("CONFIGURAÇÃO DO PROCESSADOR CONTÍNUO")
    print("=" * 60)
    
    interval = int(os.getenv('PROCESSOR_INTERVAL_MINUTES', 15))
    days_back = int(os.getenv('EMAIL_DAYS_BACK', 7))
    
    print(f"\n  ⏱️  Intervalo de Verificação: {interval} minutos")
    print(f"  📅 Busca E-mails: últimos {days_back} dias")
    print(f"  🔄 Ciclos por Dia: ~{1440 // interval} ciclos")
    print(f"  ⏳ Tempo Total por Hora: ~{(60 // interval) * 2} minutos processando")
    
    # Recomendações
    print("\n  💡 Recomendações:")
    if interval < 10:
        print("    ⚠️  Intervalo muito curto pode sobrecarregar o sistema")
    elif interval > 60:
        print("    ⚠️  Intervalo muito longo pode atrasar processamento")
    else:
        print("    ✓ Intervalo adequado")
    
    if days_back > 14:
        print("    ⚠️  Buscar muitos dias pode ser lento")
    else:
        print("    ✓ Janela de busca adequada")


def test_connection():
    """Testa conexão com serviços externos."""
    print("\n" + "=" * 60)
    print("TESTE DE CONECTIVIDADE")
    print("=" * 60)
    
    # Teste IMAP
    print("\n  📧 Testando conexão IMAP...")
    try:
        from src.services.email_reader import EmailReader
        reader = EmailReader(
            host=os.getenv('EMAIL_HOST'),
            port=int(os.getenv('EMAIL_PORT', 993)),
            user=os.getenv('EMAIL_USER'),
            password=os.getenv('EMAIL_PASSWORD'),
            folder=os.getenv('EMAIL_FOLDER', 'INBOX'),
            subject_filter=os.getenv('EMAIL_SUBJECT_FILTER', 'Novo Agendamento')
        )
        # Não precisa fazer nada, o __init__ já conecta
        print("    ✓ Conexão IMAP OK")
    except Exception as e:
        print(f"    ✗ Erro na conexão IMAP: {e}")
    
    # Teste OpenAI (simples)
    print("\n  🤖 Verificando OpenAI API Key...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key.startswith('sk-'):
        print("    ✓ OpenAI API Key parece válida")
    else:
        print("    ✗ OpenAI API Key inválida ou não configurada")
    
    # Teste MinasTaxi
    print("\n  🚕 Verificando MinasTaxi API...")
    if os.getenv('MINASTAXI_API_URL'):
        print(f"    ✓ URL configurada: {os.getenv('MINASTAXI_API_URL')}")
    else:
        print("    ✗ MinasTaxi URL não configurada")


def main():
    """Executa todas as verificações."""
    print("\n" + "🚕 " * 20)
    print("DIAGNÓSTICO DO PROCESSADOR DE TÁXI")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚕 " * 20)
    
    results = []
    
    # Verificações
    results.append(("Variáveis de Ambiente", check_environment()))
    results.append(("Banco de Dados", check_database()))
    results.append(("Arquivos de Log", check_logs()))
    check_processor_config()
    test_connection()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✓ OK" if passed else "✗ ERRO"
        print(f"  {status}: {name}")
    
    if all_passed:
        print("\n  🎉 Sistema pronto para processar pedidos!")
        print(f"\n  Para iniciar o processador:")
        print(f"    python run_processor.py")
    else:
        print("\n  ⚠️  Corrija os erros acima antes de executar o processador")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
