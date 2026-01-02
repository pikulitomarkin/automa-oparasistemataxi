#!/usr/bin/env python3
"""
Script para verificar detalhes dos pedidos falhados.
"""
import os
from dotenv import load_dotenv
from src.services.database import DatabaseManager
from src.models import OrderStatus

load_dotenv()

def main():
    """Verifica pedidos falhados e mostra detalhes dos erros."""
    print("=" * 80)
    print("🔍 VERIFICAÇÃO DE PEDIDOS FALHADOS")
    print("=" * 80)
    print()
    
    db = DatabaseManager()
    
    # Busca pedidos falhados
    failed_orders = db.get_orders_by_status(OrderStatus.FAILED)
    manual_review = db.get_orders_by_status(OrderStatus.MANUAL_REVIEW)
    
    print(f"📊 Total de pedidos com problemas:")
    print(f"  ❌ FAILED: {len(failed_orders)}")
    print(f"  ⚠️  MANUAL_REVIEW: {len(manual_review)}")
    print()
    
    if failed_orders:
        print("=" * 80)
        print("❌ PEDIDOS COM STATUS FAILED:")
        print("=" * 80)
        
        for i, order in enumerate(failed_orders, 1):
            print(f"\n📋 Pedido #{i} (ID: {order.id})")
            print(f"   Email ID: {order.email_id}")
            print(f"   Passageiro: {order.passenger_name}")
            print(f"   Telefone: {order.phone}")
            print(f"   Origem: {order.pickup_address}")
            print(f"   Destino: {order.dropoff_address}")
            print(f"   Horário: {order.pickup_time}")
            print(f"   Criado em: {order.created_at}")
            print(f"   🔴 ERRO: {order.error_message}")
            print("-" * 80)
    
    if manual_review:
        print("\n" + "=" * 80)
        print("⚠️  PEDIDOS EM MANUAL_REVIEW:")
        print("=" * 80)
        
        for i, order in enumerate(manual_review, 1):
            print(f"\n📋 Pedido #{i} (ID: {order.id})")
            print(f"   Email ID: {order.email_id}")
            print(f"   Passageiro: {order.passenger_name}")
            print(f"   Telefone: {order.phone}")
            print(f"   Origem: {order.pickup_address}")
            print(f"   Destino: {order.dropoff_address}")
            print(f"   Horário: {order.pickup_time}")
            print(f"   Criado em: {order.created_at}")
            print(f"   ⚠️  MOTIVO: {order.error_message if order.error_message else 'Não especificado'}")
            print("-" * 80)
    
    if not failed_orders and not manual_review:
        print("✅ Nenhum pedido com problemas encontrado!")
    
    print("\n" + "=" * 80)
    print("📌 RESUMO DAS ESTATÍSTICAS:")
    print("=" * 80)
    stats = db.get_statistics()
    for key, value in stats.items():
        if key != 'total':
            print(f"   {key.upper()}: {value}")
    print(f"   TOTAL: {stats['total']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
