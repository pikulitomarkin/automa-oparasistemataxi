#!/usr/bin/env python3
"""
Teste específico para validar se o sistema no Railway funciona com as correções SSL.
Este teste simula exatamente o que acontece durante o processamento de email.
"""
import os
import logging
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_railway_ssl_config():
    """
    Testa se as configurações SSL funcionam no ambiente Railway.
    """
    print("🚀 TESTE CONFIGURAÇÃO SSL RAILWAY")
    print("=" * 50)
    
    try:
        # Importa exatamente como o sistema faz
        from src.services.minastaxi_client import MinasTaxiClient
        
        print("✅ Import MinasTaxiClient successful")
        
        # Cria cliente exatamente como o processor faz
        client = MinasTaxiClient(
            api_url=os.getenv('MINASTAXI_API_URL', 'https://vm2c.taxifone.com.br:11048'),
            user_id=os.getenv('MINASTAXI_USER_ID'),
            password=os.getenv('MINASTAXI_PASSWORD'),
            auth_header=os.getenv('MINASTAXI_AUTH_HEADER', 'Basic Original'),
            timeout=int(os.getenv('MINASTAXI_TIMEOUT', 30)),
            max_retries=int(os.getenv('MINASTAXI_RETRY_ATTEMPTS', 3))
        )
        
        print("✅ MinasTaxiClient initialized")
        print(f"📡 API URL: {os.getenv('MINASTAXI_API_URL')}")
        print(f"👤 User ID: {os.getenv('MINASTAXI_USER_ID')}")
        print(f"🔐 Auth Header: {os.getenv('MINASTAXI_AUTH_HEADER')}")
        
        # Testa conectividade usando adapter SSL
        print("\n🔍 Testando conectividade com adapter SSL...")
        
        success = client.test_connection()
        
        if success:
            print("✅ SUCESSO: Adapter SSL funcionando!")
            print("🎯 Sistema pronto para dispatch real")
            return True
        else:
            print("❌ FALHA: Problema de conectividade SSL")
            return False
            
    except ImportError as e:
        print(f"❌ ERRO IMPORT: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """
    Verifica se todas as variáveis necessárias estão configuradas.
    """
    print("\n🔧 TESTE VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    required_vars = [
        'MINASTAXI_API_URL',
        'MINASTAXI_USER_ID', 
        'MINASTAXI_PASSWORD',
        'MINASTAXI_AUTH_HEADER'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ VARIÁVEIS FALTANDO: {missing_vars}")
        return False
    else:
        print("\n✅ Todas as variáveis configuradas!")
        return True

def main():
    """
    Executa todos os testes de validação.
    """
    print("🎯 VALIDAÇÃO CONFIGURAÇÃO SISTEMA RAILWAY")
    print("=" * 60)
    print("🔧 Verificando se sistema está pronto para produção")
    print()
    
    # Teste 1: Variáveis de ambiente
    env_ok = test_environment_variables()
    
    # Teste 2: Configuração SSL (só se env OK)
    if env_ok:
        ssl_ok = test_railway_ssl_config()
    else:
        ssl_ok = False
        print("\n⚠️ PULANDO teste SSL - variáveis faltando")
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print("=" * 60)
    
    tests_results = [
        ("🔧 Variáveis de Ambiente", env_ok),
        ("🔒 Configuração SSL/TLS", ssl_ok)
    ]
    
    for test_name, result in tests_results:
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    success_rate = sum([env_ok, ssl_ok]) / 2 * 100
    print(f"\n🎯 Taxa de sucesso: {success_rate:.0f}%")
    
    if success_rate == 100:
        print("\n🎉 SISTEMA 100% PRONTO PARA PRODUÇÃO!")
        print("📧 Pode enviar email de teste agora")
        print("🚀 API MinasTaxi funcionará corretamente")
    elif success_rate >= 50:
        print("\n⚠️ SISTEMA PARCIALMENTE PRONTO")
        print("🔧 Corrigir problemas antes do teste")
    else:
        print("\n🚨 SISTEMA NÃO PRONTO")
        print("❌ Configurar variáveis e SSL antes de testar")

if __name__ == "__main__":
    main()