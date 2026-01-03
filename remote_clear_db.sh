#!/bin/bash
# Script para limpar banco no Railway

echo "🗑️ Limpando banco de dados..."
python3 -c "
import sqlite3
import os

db_path = os.getenv('DATABASE_PATH', '/data/taxi_orders.db')
print(f'📊 Banco: {db_path}')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Conta orders
cursor.execute('SELECT COUNT(*) FROM orders')
total = cursor.fetchone()[0]
print(f'Total de orders ANTES: {total}')

# Mostra por status
cursor.execute('SELECT status, COUNT(*) FROM orders GROUP BY status')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Limpa banco
cursor.execute('DELETE FROM orders')
conn.commit()
print('✅ Banco limpo!')

cursor.execute('SELECT COUNT(*) FROM orders')
total_after = cursor.fetchone()[0]
print(f'Total DEPOIS: {total_after}')

conn.close()
"
