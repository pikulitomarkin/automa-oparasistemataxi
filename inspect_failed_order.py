#!/usr/bin/env python
"""
Script para inspecionar e reprocessar pedidos falhados.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.services.database import DatabaseManager
from src.models import OrderStatus

def inspect_failed_orders():
    """Mostra detalhes de todos os pedidos falhados."""
    db = DatabaseManager(os.getenv('DATABASE_PATH', 'data/taxi_orders.db'))
    
    print("\n" + "=" * 80)
    print("PEDIDOS COM FALHA OU EM REVISÃO MANUAL")
    print("=" * 80 + "\n")
    
    # Busca pedidos falhados
    failed = db.get_orders_by_status(OrderStatus.FAILED)
    manual = db.get_orders_by_status(OrderStatus.MANUAL_REVIEW)
    
    all_problem_orders = failed + manual
    
    if not all_problem_orders:
        print("✅ Nenhum pedido com problemas encontrado!")
        return
    
    for i, order in enumerate(all_problem_orders, 1):
        print(f"\n{'='*80}")
        print(f"PEDIDO #{i} - ID: {order.id}")
        print(f"{'='*80}")
        print(f"📧 Email UID: {order.email_id}")
        print(f"🚨 Status: {order.status.value}")
        print(f"❌ Erro: {order.error_message or 'Nenhum erro registrado'}")
        print(f"👤 Passageiro: {order.passenger_name or 'N/A'}")
        print(f"📱 Telefone: {order.phone or 'N/A'}")
        print(f"📍 Coleta: {order.pickup_address or 'N/A'}")
        print(f"🎯 Destino: {order.dropoff_address or 'N/A'}")
        print(f"⏰ Horário: {order.pickup_time or 'N/A'}")
        
        if order.pickup_lat and order.pickup_lng:
            print(f"🗺️  Coords Coleta: {order.pickup_lat}, {order.pickup_lng}")
        
        if order.passengers:
            print(f"👥 Múltiplos Passageiros: {len(order.passengers)} passageiros")
        
        print(f"\n📄 E-mail Original (primeiras 300 chars):")
        print("-" * 80)
        if order.raw_email_body:
            print(order.raw_email_body[:300] + "...")
        else:
            print("(não disponível)")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {len(all_problem_orders)} pedidos com problemas")
    print("=" * 80 + "\n")
    
    # Menu de ações
    print("AÇÕES DISPONÍVEIS:")
    print("1. Deletar um pedido específico (para reprocessar do e-mail)")
    print("2. Deletar TODOS os pedidos falhados")
    print("3. Apenas visualizar (nenhuma ação)")
    print()
    
    choice = input("Escolha uma opção (1/2/3): ").strip()
    
    if choice == "1":
        order_id = input("Digite o ID do pedido para deletar: ").strip()
        try:
            order_id = int(order_id)
            # Encontra o pedido
            order_to_delete = next((o for o in all_problem_orders if o.id == order_id), None)
            if order_to_delete:
                db.delete_order(order_id)
                print(f"\n✅ Pedido {order_id} (Email UID={order_to_delete.email_id}) deletado!")
                print("🔄 O próximo ciclo do processador irá reprocessá-lo do e-mail.")
            else:
                print(f"\n❌ Pedido {order_id} não encontrado na lista.")
        except ValueError:
            print("\n❌ ID inválido!")
    
    elif choice == "2":
        confirm = input(f"\n⚠️  Deletar TODOS os {len(all_problem_orders)} pedidos? (sim/não): ").strip().lower()
        if confirm == "sim":
            for order in all_problem_orders:
                db.delete_order(order.id)
            print(f"\n✅ {len(all_problem_orders)} pedidos deletados!")
            print("🔄 O processador irá reprocessá-los do e-mail.")
        else:
            print("\n❌ Operação cancelada.")
    
    else:
        print("\n✅ Nenhuma ação realizada.")

if __name__ == "__main__":
    inspect_failed_orders()
