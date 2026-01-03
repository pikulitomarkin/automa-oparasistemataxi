#!/usr/bin/env python3
"""
Script para limpar o banco de dados no Railway.
Remove todas as orders para começar testes do zero.
"""
import os
import sqlite3
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

def clear_database():
    """Limpa todas as tabelas do banco de dados."""
    db_path = os.getenv('DATABASE_PATH', '/data/taxi_orders.db')
    
    print(f"🗑️  Limpando banco de dados: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Conta orders antes de limpar
        cursor.execute("SELECT COUNT(*) FROM orders")
        count_before = cursor.fetchone()[0]
        print(f"📊 Orders no banco ANTES: {count_before}")
        
        # Limpa tabela de orders
        cursor.execute("DELETE FROM orders")
        conn.commit()
        
        # Conta orders depois de limpar
        cursor.execute("SELECT COUNT(*) FROM orders")
        count_after = cursor.fetchone()[0]
        print(f"📊 Orders no banco DEPOIS: {count_after}")
        
        print("✅ Banco de dados limpo com sucesso!")
        print("🎯 Agora você pode enviar emails de teste para validar o sistema")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")
        raise

if __name__ == "__main__":
    clear_database()
