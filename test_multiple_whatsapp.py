"""
Teste para validar envio de WhatsApp para múltiplos passageiros.
"""
import os
import sys
from datetime import datetime, timedelta

# Adiciona src ao path ANTES de carregar .env
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from models.order import Order, OrderStatus
from services.whatsapp_notifier import WhatsAppNotifier

def test_multiple_passengers_whatsapp():
    """
    Simula um pedido com 3 passageiros e verifica se o WhatsApp
    é enviado para todos os telefones individuais.
    """
    
    # Cria notificador WhatsApp
    whatsapp = WhatsAppNotifier(
        api_url=os.getenv('EVOLUTION_API_URL'),
        api_key=os.getenv('EVOLUTION_API_KEY'),
        instance_name=os.getenv('EVOLUTION_INSTANCE_NAME'),
        auth_header_name=os.getenv('EVOLUTION_AUTH_HEADER_NAME', 'apikey')
    )
    
    # Simula um pedido com 3 passageiros
    order = Order(
        id=999,
        passenger_name="Gasparino Rodrigues da Silva",
        phone="31999999926",  # Telefone do primeiro passageiro
        pickup_address="RUA Jorge Dias de Oliva, 172, Vespasiano, MG",
        dropoff_address="Delp Engenharia Vespasiano",
        pickup_time=datetime.now() + timedelta(hours=2),
        status=OrderStatus.DISPATCHED,
        passengers=[
            {
                "name": "Gasparino Rodrigues da Silva",
                "phone": "31999999926",
                "address": "RUA Jorge Dias de Oliva, 172, Vespasiano, MG"
            },
            {
                "name": "Timoteo de Almeida Batalha",
                "phone": "31988887777",  # Telefone diferente
                "address": "RUA Ceará, 200, Celvia, Vespasiano, MG"
            },
            {
                "name": "Brendo dos Santos Silva",
                "phone": "31977776666",  # Telefone diferente
                "address": "AV. Alcino Gonçalves Cota, 563, Bom Jesus, Matozinhos, MG"
            }
        ]
    )
    
    print("=" * 80)
    print("TESTE: Envio de WhatsApp para Múltiplos Passageiros")
    print("=" * 80)
    print(f"\nPedido ID: {order.id}")
    print(f"Passageiro Principal: {order.passenger_name} ({order.phone})")
    print(f"Total de Passageiros: {len(order.passengers)}")
    
    # Simula a lógica do processor
    passengers_to_notify = []
    
    # Adiciona passageiro principal
    if order.phone:
        passengers_to_notify.append({
            'name': order.passenger_name or "Cliente",
            'phone': order.phone
        })
        print(f"\n✅ Adicionado: {order.passenger_name} - {order.phone}")
    
    # Adiciona passageiros adicionais
    if order.passengers:
        for passenger in order.passengers:
            if passenger.get('phone'):
                # Evita duplicatas
                if not any(p['phone'] == passenger['phone'] for p in passengers_to_notify):
                    passengers_to_notify.append({
                        'name': passenger.get('name', 'Cliente'),
                        'phone': passenger['phone']
                    })
                    print(f"✅ Adicionado: {passenger['name']} - {passenger['phone']}")
                else:
                    print(f"⚠️ Duplicado (ignorado): {passenger['name']} - {passenger['phone']}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL DE MENSAGENS A ENVIAR: {len(passengers_to_notify)}")
    print(f"{'='*80}\n")
    
    # Envia mensagem para cada passageiro
    whatsapp_sent_count = 0
    for idx, passenger in enumerate(passengers_to_notify, 1):
        print(f"\n[{idx}/{len(passengers_to_notify)}] Enviando para {passenger['name']}...")
        print(f"    Telefone: {passenger['phone']}")
        
        try:
            # Normaliza o telefone
            normalized = whatsapp.normalize_phone(passenger['phone'])
            print(f"    Normalizado: {normalized}")
            
            # Envia mensagem
            response = whatsapp.send_message(
                name=passenger['name'],
                phone=passenger['phone'],
                destination=order.dropoff_address,
                status="Sucesso"
            )
            
            if response.get('success'):
                whatsapp_sent_count += 1
                print(f"    ✅ Enviado com sucesso!")
                if response.get('message_id'):
                    print(f"    Message ID: {response['message_id']}")
            else:
                print(f"    ❌ Falha: {response.get('error')}")
                
        except Exception as e:
            print(f"    ❌ Erro: {e}")
    
    print(f"\n{'='*80}")
    print(f"RESULTADO FINAL")
    print(f"{'='*80}")
    print(f"✅ Mensagens enviadas: {whatsapp_sent_count}/{len(passengers_to_notify)}")
    
    if whatsapp_sent_count == len(passengers_to_notify):
        print(f"🎉 SUCESSO: Todos os passageiros foram notificados!")
    elif whatsapp_sent_count > 0:
        print(f"⚠️ PARCIAL: {whatsapp_sent_count} de {len(passengers_to_notify)} receberam")
    else:
        print(f"❌ FALHA: Nenhuma mensagem foi enviada")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_multiple_passengers_whatsapp()
