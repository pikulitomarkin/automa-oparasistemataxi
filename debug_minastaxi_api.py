#!/usr/bin/env python3
"""
Debug script para testar conexão com API MinasTaxi.
Testa conectividade, credenciais e SSL/TLS.
"""
import os
import requests
import ssl
import urllib3
from dotenv import load_dotenv
from src.services.minastaxi_client import MinasTaxiClient

# Carrega .env
load_dotenv()

def test_basic_connectivity():
    """Testa conectividade básica com o servidor."""
    print("🔍 TESTE 1: Conectividade Básica")
    print("=" * 50)
    
    api_url = os.getenv('MINASTAXI_API_URL', 'https://vm2c.taxifone.com.br:11048')
    
    try:
        # Desabilita warnings SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Teste simples de conectividade
        response = requests.get(
            api_url,
            timeout=10,
            verify=False
        )
        
        print(f"✅ Servidor acessível!")
        print(f"📡 Status: {response.status_code}")
        print(f"🌐 Headers: {dict(response.headers)}")
        print(f"📄 Content: {response.text[:200]}...")
        
        return True
        
    except requests.exceptions.SSLError as e:
        print(f"❌ Erro SSL: {e}")
        return False
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Timeout conectando ao servidor")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_ssl_compatibility():
    """Testa compatibilidade SSL/TLS."""
    print("\n🔒 TESTE 2: Compatibilidade SSL/TLS")
    print("=" * 50)
    
    hostname = "vm2c.taxifone.com.br"
    port = 11048
    
    try:
        # Cria contexto SSL permissivo
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        # Permite TLS legado
        context.options &= ~ssl.OP_NO_SSLv2
        context.options &= ~ssl.OP_NO_SSLv3
        context.options &= ~ssl.OP_NO_TLSv1
        context.options &= ~ssl.OP_NO_TLSv1_1
        context.set_ciphers('DEFAULT:@SECLEVEL=1')
        
        # Conecta com SSL
        with context.wrap_socket(socket.socket(), server_hostname=hostname) as sock:
            sock.settimeout(10)
            sock.connect((hostname, port))
            
            print(f"✅ SSL/TLS conectado com sucesso!")
            print(f"🔐 Versão TLS: {sock.version()}")
            print(f"🔗 Cipher: {sock.cipher()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro SSL: {e}")
        return False

def test_api_endpoint():
    """Testa endpoint específico com payload real."""
    print("\n🚀 TESTE 3: Endpoint rideCreate")
    print("=" * 50)
    
    # Carrega credenciais
    api_url = os.getenv('MINASTAXI_API_URL')
    user_id = os.getenv('MINASTAXI_USER_ID')
    password = os.getenv('MINASTAXI_PASSWORD')
    auth_header = os.getenv('MINASTAXI_AUTH_HEADER')
    
    print(f"🔧 API URL: {api_url}")
    print(f"👤 User ID: {user_id}")
    print(f"🔑 Password: {password}")
    print(f"🔐 Auth Header: {auth_header}")
    
    if not all([api_url, user_id, password]):
        print("❌ Credenciais não configuradas!")
        return False
    
    # Payload mínimo para teste
    payload = {
        "partner": "1",
        "user": user_id,
        "password": password,
        "request_id": "TEST20251230DEBUG",
        "pickup_time": "1735516800",  # 30/12/2024 00:00:00
        "category": "taxi",
        "passengers_no": 1,
        "suitcases_no": 0,
        "passenger_note": "TESTE DEBUG API",
        "passenger_name": "TESTE SISTEMA",
        "passenger_phone_number": "31999999999",
        "payment_type": "ONLINE_PAYMENT",
        "users": [
            {
                "id": 1,
                "sequence": 1,
                "name": "TESTE SISTEMA",
                "phone": "31999999999",
                "pickup": {
                    "address": "Rua Rio de Janeiro, 500, Centro, Belo Horizonte, MG",
                    "city": "Belo Horizonte",
                    "state": "MG",
                    "postal_code": "",
                    "lat": "-19.918101",
                    "lng": "-43.938340"
                }
            }
        ]
    }
    
    headers = {
        'authorization': auth_header or 'Basic Original',
        'Content-Type': 'application/json',
        'User-Agent': 'TaxiAutomationSystem-Debug/1.0'
    }
    
    endpoint = f"{api_url}/rideCreate"
    
    try:
        print(f"📤 Enviando para: {endpoint}")
        print(f"📋 Headers: {headers}")
        print(f"📦 Payload: {payload}")
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"\n📥 RESPOSTA:")
        print(f"🔢 Status: {response.status_code}")
        print(f"🗂️ Headers: {dict(response.headers)}")
        print(f"📄 Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ API respondeu corretamente!")
            return True
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Problema de autenticação/autorização")
            return False
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_with_client():
    """Testa usando o cliente oficial."""
    print("\n🎯 TESTE 4: Cliente MinasTaxiClient")
    print("=" * 50)
    
    try:
        client = MinasTaxiClient(
            api_url=os.getenv('MINASTAXI_API_URL'),
            user_id=os.getenv('MINASTAXI_USER_ID'),
            password=os.getenv('MINASTAXI_PASSWORD'),
            auth_header=os.getenv('MINASTAXI_AUTH_HEADER')
        )
        
        # Teste de conectividade
        print("🔍 Testando conectividade...")
        is_connected = client.test_connection()
        
        if is_connected:
            print("✅ Cliente conectado com sucesso!")
        else:
            print("❌ Falha na conexão do cliente")
        
        return is_connected
        
    except Exception as e:
        print(f"❌ Erro no cliente: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 DIAGNÓSTICO API MINASTAXI")
    print("=" * 50)
    print("🎯 Verificando conexão, SSL, credenciais e endpoints")
    print()
    
    results = []
    
    # Teste 1: Conectividade
    results.append(test_basic_connectivity())
    
    # Teste 2: SSL (só se conectividade OK)
    if results[0]:
        results.append(test_ssl_compatibility())
    else:
        results.append(False)
    
    # Teste 3: API Endpoint
    results.append(test_api_endpoint())
    
    # Teste 4: Cliente oficial
    results.append(test_with_client())
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 50)
    
    tests = [
        "🌐 Conectividade Básica",
        "🔒 SSL/TLS Compatibilidade", 
        "🚀 API Endpoint /rideCreate",
        "🎯 Cliente MinasTaxiClient"
    ]
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n🎯 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate < 50:
        print("\n🚨 PROBLEMA CRÍTICO - API inacessível ou mal configurada")
    elif success_rate < 100:
        print("\n⚠️ PROBLEMA PARCIAL - Verificar configurações específicas")
    else:
        print("\n🎉 TUDO OK - API funcionando perfeitamente!")

if __name__ == "__main__":
    import socket
    main()