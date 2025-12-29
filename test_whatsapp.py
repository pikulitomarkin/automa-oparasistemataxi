"""
Script de teste para WhatsApp (Evolution API).
Envia uma mensagem de teste para verificar conectividade.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Adiciona diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.whatsapp_notifier import WhatsAppNotifier

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Testa envio de mensagem WhatsApp."""
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configurações
    api_url = os.getenv('EVOLUTION_API_URL')
    api_key = os.getenv('EVOLUTION_API_KEY')
    instance_name = os.getenv('EVOLUTION_INSTANCE_NAME')
    
    print("\n🚖 TESTE DE WHATSAPP (Evolution API)\n")
    print(f"📡 URL: {api_url}")
    print(f"🔑 Instance: {instance_name}")
    print("-" * 50)
    
    # Valida configurações
    if not all([api_url, api_key, instance_name]):
        print("❌ ERRO: Variáveis de ambiente não configuradas!")
        print("\nVerifique no .env:")
        print("- EVOLUTION_API_URL")
        print("- EVOLUTION_API_KEY")
        print("- EVOLUTION_INSTANCE_NAME")
        return
    
    # Solicita número de telefone
    print("\n📱 Digite o número para enviar mensagem de teste:")
    print("   Formato: (31) 98888-8888 ou 31988888888")
    phone = input("   Telefone: ").strip()
    
    if not phone:
        print("❌ Telefone não informado!")
        return
    
    # Solicita nome
    name = input("   Nome (opcional): ").strip() or "Cliente Teste"
    
    print("\n🔄 Inicializando WhatsApp Notifier...")
    
    try:
        # Cria notificador
        notifier = WhatsAppNotifier(
            api_url=api_url,
            api_key=api_key,
            instance_name=instance_name
        )
        
        # Envia mensagem de teste
        print(f"📤 Enviando mensagem de teste para {phone}...")
        
        result = notifier.send_message(
            name=name,
            phone=phone,
            destination="Aeroporto de Confins",
            status="Sucesso"
        )
        
        if result.get('success'):
            print("\n✅ MENSAGEM ENVIADA COM SUCESSO!")
            print(f"   Message ID: {result.get('message_id', 'N/A')}")
            print(f"   Telefone normalizado: {result['payload']['number']}")
        else:
            print("\n❌ FALHA AO ENVIAR MENSAGEM")
            print(f"   Erro: {result.get('error', 'Desconhecido')}")
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\nVerifique:")
        print("1. Se o Evolution API está rodando")
        print("2. Se a instância está conectada (QR Code escaneado)")
        print("3. Se a API Key está correta")
        print("4. Se a URL está acessível")

if __name__ == '__main__':
    main()
